#!/usr/bin/env python3
"""Dual Momentum 双动量策略 v2。

基于 Gary Antonacci 的 Dual Momentum 框架，适配比特币单标的CTA交易。

核心机制:
  - 绝对动量: close > SMA(momentum_period) — 判断趋势方向
  - 相对动量: ROC(roc_period) > 0 — 判断趋势强度
  - 双条件同时满足 → 入场做多
  - 仅 ATR 追踪止损离场（不含 SMA 离场，避免频繁进出）
  - 离场后冷却期，防止 whip-saw
  - 仅做多（Long-Only）
"""

from __future__ import annotations

from typing import Any

from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.constant import Interval
from vnpy_ctastrategy import CtaTemplate, BarGenerator, ArrayManager


class DualMomentumStrategy(CtaTemplate):
    """Dual Momentum 双动量策略 v2。

    信号K线上运行：绝对动量（SMA）+ 相对动量（ROC>0）双过滤入场，
    ATR 追踪止损离场。仅做多。
    """

    author: str = "CTA Agent"

    # ── 策略参数 ──
    momentum_period: int = 100     # 绝对动量 SMA 周期
    roc_period: int = 50           # 相对动量 ROC 周期
    atr_period: int = 20           # ATR 周期
    atr_stop_mult: float = 3.0     # ATR 追踪止损倍数
    cooldown_bars: int = 20        # 离场后冷却 bar 数
    fixed_size: int = 1            # 固定仓位
    use_dynamic_size: bool = False # 是否使用动态仓位
    position_multiplier: float = 0.005  # 动态仓位乘数
    bar_interval_minutes: int = 240  # K线周期（4h）

    # ── 策略变量 ──
    sma_value: float = 0.0
    roc_value: float = 0.0
    atr_value: float = 0.0
    trailing_long: float = 0.0     # 多头追踪止损价
    entry_price: float = 0.0
    highest_since_entry: float = 0.0
    bars_since_exit: int = 999     # 离场后计数（初始大值允许立即入场）

    parameters: list[str] = [
        "momentum_period", "roc_period", "atr_period",
        "atr_stop_mult", "cooldown_bars", "fixed_size",
        "use_dynamic_size", "position_multiplier",
        "bar_interval_minutes",
    ]
    variables: list[str] = [
        "sma_value", "roc_value", "atr_value",
        "trailing_long", "entry_price", "highest_since_entry",
        "bars_since_exit",
    ]

    def __init__(self, cta_engine: Any, strategy_name: str,
                 vt_symbol: str, setting: dict[str, Any]) -> None:
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        if self.bar_interval_minutes % 60 == 0:
            hours: int = self.bar_interval_minutes // 60
            self.bg = BarGenerator(
                self.on_bar, hours, self.on_window_bar, Interval.HOUR,
            )
        else:
            self.bg = BarGenerator(
                self.on_bar, self.bar_interval_minutes, self.on_window_bar,
                Interval.MINUTE,
            )

        size: int = max(self.momentum_period, self.roc_period,
                        self.atr_period) + 10
        self.am = ArrayManager(size)

    def on_init(self) -> None:
        """策略初始化。"""
        self.write_log("DualMomentum 策略初始化")
        self.load_bar(10)

    def on_start(self) -> None:
        """策略启动。"""
        self.write_log("DualMomentum 策略启动")

    def on_stop(self) -> None:
        """策略停止。"""
        self.write_log("DualMomentum 策略停止")

    def on_tick(self, tick: TickData) -> None:
        """Tick 推送。"""
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        """1m K线推送 → 喂给 BarGenerator。"""
        self.bg.update_bar(bar)

    def on_window_bar(self, bar: BarData) -> None:
        """信号K线主逻辑。"""
        self.cancel_all()

        am = self.am
        am.update_bar(bar)
        if not am.inited:
            return

        # ── 计算指标 ──
        self.sma_value = float(am.sma(self.momentum_period, array=True)[-1])
        self.roc_value = float(am.roc(self.roc_period, array=True)[-1])
        self.atr_value = float(am.atr(self.atr_period, array=True)[-1])

        # ── 信号判断 ──
        abs_momentum: bool = bar.close_price > self.sma_value
        rel_momentum: bool = self.roc_value > 0.0
        dual_signal: bool = abs_momentum and rel_momentum

        current_pos: int = self.pos

        # ── 离场后冷却计数 ──
        if current_pos == 0:
            self.bars_since_exit += 1

        # ── 计算仓位 ──
        if self.use_dynamic_size and self.atr_value > 0:
            trade_size: int = max(
                1,
                int(self.cta_engine.capital / self.atr_value
                    * self.position_multiplier),
            )
        else:
            trade_size = self.fixed_size

        # ── 入场逻辑 ──
        if current_pos == 0:
            if dual_signal and self.bars_since_exit >= self.cooldown_bars:
                price: float = bar.close_price
                self.buy(price, trade_size)
                self.entry_price = price
                self.highest_since_entry = price
                self.trailing_long = price - self.atr_stop_mult * self.atr_value
                self.bars_since_exit = 0
        else:
            # ── 持仓中：更新追踪止损 ──
            self.highest_since_entry = max(self.highest_since_entry,
                                           bar.high_price)
            new_stop: float = (self.highest_since_entry
                               - self.atr_stop_mult * self.atr_value)
            self.trailing_long = max(self.trailing_long, new_stop)

            # ── 离场：仅 ATR 追踪止损触发 ──
            if bar.close_price <= self.trailing_long:
                self.sell(bar.close_price, abs(current_pos))
                self.entry_price = 0.0
                self.highest_since_entry = 0.0
                self.trailing_long = 0.0

        self.put_event()

    def on_order(self, order: OrderData) -> None:
        """委托回调。"""
        pass

    def on_trade(self, trade: TradeData) -> None:
        """成交回调。"""
        self.put_event()

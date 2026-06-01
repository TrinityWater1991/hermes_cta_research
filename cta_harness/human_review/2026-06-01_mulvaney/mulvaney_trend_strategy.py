#!/usr/bin/env python3
"""Mulvaney Donchian 趋势跟踪策略。

逆向工程 Paul Mulvaney 的 26 年长线趋势跟踪系统，适配加密单标的。
核心机制:
  - Donchian 通道突破入场（仅做多）
  - 固定初始止损（通道宽度 × stop_offset）
  - Donchian 中线单向追踪止损
  - 动态仓位（capital/ATR × multiplier）
"""

from __future__ import annotations

from typing import Any

from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.constant import Interval
from vnpy_ctastrategy import CtaTemplate, BarGenerator, ArrayManager


class MulvaneyTrendStrategy(CtaTemplate):
    """Mulvaney Donchian 趋势跟踪策略。

    2h K线上运行：Donchian通道突破入场 → 固定初始止损 →
    浮盈达标后切换中线追踪止损。仅做多。
    """

    author: str = "CTA Agent"

    # ── 策略参数 ──
    donchian_period: int = 200
    stop_offset: float = 0.33
    trail_trigger_mult: float = 1.0
    atr_period: int = 20
    fixed_size: int = 1
    use_dynamic_size: bool = False
    position_multiplier: float = 0.005
    bar_interval_minutes: int = 120

    # ── 策略变量 ──
    donchian_high: float = 0.0
    donchian_low: float = 0.0
    donchian_mid: float = 0.0
    channel_width: float = 0.0
    initial_stop: float = 0.0
    trail_stop: float = 0.0
    trail_active: bool = False
    entry_price: float = 0.0
    atr_value: float = 0.0
    bars_in_trade: int = 0

    parameters: list[str] = [
        "donchian_period", "stop_offset", "trail_trigger_mult",
        "atr_period", "fixed_size", "use_dynamic_size",
        "position_multiplier", "bar_interval_minutes",
    ]
    variables: list[str] = [
        "donchian_high", "donchian_low", "donchian_mid",
        "channel_width", "initial_stop", "trail_stop",
        "trail_active", "entry_price", "atr_value", "bars_in_trade",
    ]

    def __init__(self, cta_engine: Any, strategy_name: str,
                 vt_symbol: str, setting: dict[str, Any]) -> None:
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        # vnpy BarGenerator 分K线限制：
        # - MINUTE: 仅支持整除60的窗口 (2,3,5,6,10,15,20,30,60)
        # - HOUR: 任意整数窗口
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
        size: int = max(self.donchian_period, self.atr_period) + 10
        self.am = ArrayManager(size)

    def on_init(self) -> None:
        self.write_log("MulvaneyTrend 策略初始化")
        self.load_bar(10)

    def on_start(self) -> None:
        self.write_log("MulvaneyTrend 策略启动")

    def on_stop(self) -> None:
        self.write_log("MulvaneyTrend 策略停止")

    def on_tick(self, tick: TickData) -> None:
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        self.bg.update_bar(bar)

    def on_window_bar(self, bar: BarData) -> None:
        """2h K线主逻辑。"""
        self.cancel_all()
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        self._update_indicators()
        if self.pos == 0:
            self._handle_no_position(bar)
        elif self.pos > 0:
            self._handle_long_position(bar)
        self.put_event()

    # ── 指标计算 ──

    def _update_indicators(self) -> None:
        """计算 Donchian 通道和 ATR。

        通道基于过去 N 根 K线计算（不含当前 bar），
        避免当前 bar 的 close 永远无法突破自己的 high。
        """
        n: int = self.donchian_period
        am: ArrayManager = self.am
        # 排除当前 bar（索引 -1），用过去 n 根 bar 计算通道
        self.donchian_high = float(max(am.high[-(n + 1):-1]))
        self.donchian_low = float(min(am.low[-(n + 1):-1]))
        self.donchian_mid = (self.donchian_high + self.donchian_low) / 2.0
        self.channel_width = self.donchian_high - self.donchian_low
        self.atr_value = am.atr(self.atr_period)

    # ── 仓位计算 ──

    def _get_size(self) -> int:
        """动态或固定仓位。"""
        if not self.use_dynamic_size:
            return self.fixed_size
        if self.atr_value <= 0:
            return 1
        capital: float = 200000.0
        dynamic: float = (capital / self.atr_value) * self.position_multiplier
        return max(1, int(dynamic))

    # ── 入场逻辑 ──

    def _handle_no_position(self, bar: BarData) -> None:
        """空仓时检测 Donchian 通道上突破。"""
        if bar.close_price < self.donchian_high:
            return
        if self.channel_width <= 0:
            return
        # 入场
        size: int = self._get_size()
        self.buy(bar.close_price, size)
        self.entry_price = bar.close_price
        self.bars_in_trade = 0
        # 初始固定止损
        self.initial_stop = (
            self.donchian_high - self.channel_width * self.stop_offset
        )
        self.trail_stop = self.initial_stop
        self.trail_active = False

    # ── 持仓管理 ──

    def _handle_long_position(self, bar: BarData) -> None:
        """持仓中：更新追踪止损，检测离场。"""
        self.bars_in_trade += 1

        # 判断是否激活追踪止损
        if not self.trail_active and self.channel_width > 0:
            trigger_price: float = (
                self.entry_price + self.channel_width * self.trail_trigger_mult
            )
            if bar.close_price >= trigger_price:
                self.trail_active = True

        # 更新止损价
        if self.trail_active:
            new_stop: float = self.donchian_mid
            if new_stop > self.trail_stop:
                self.trail_stop = new_stop
        else:
            # 未激活追踪时，初始止损也单向移动（取初始止损和中线中较高者）
            if self.donchian_mid > self.trail_stop:
                self.trail_stop = self.donchian_mid

        # 止损离场
        if bar.close_price <= self.trail_stop:
            self.sell(bar.close_price, abs(self.pos))

    # ── 委托/成交回调 ──

    def on_order(self, order: OrderData) -> None:
        pass

    def on_trade(self, trade: TradeData) -> None:
        self.put_event()

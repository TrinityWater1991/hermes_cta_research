#!/usr/bin/env python3
"""AlphaFlow v2 — 增加长期EMA方向过滤 + 支持自定义K线周期。

v2变更:
  - 增加filter_ema_period参数：只在长期EMA方向交易
  - 支持通过bar_interval_minutes自定义合成K线周期（默认60=1h）
  - 牛市filter: close > filter_ema 时才允许做多
  - 熊市filter: close < filter_ema 时不允许任何多头操作
"""

from __future__ import annotations

from collections import deque
from typing import Any

import numpy as np
from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy_ctastrategy import (
    CtaTemplate,
    BarGenerator,
    ArrayManager,
)


class AlphaFlowStrategy(CtaTemplate):
    """Alpha Flow 波动率包络策略 v2.

    双EMA(HLC/3)基线 + 基线波动率包络 + 收盘价体制锁定 + 长期EMA方向过滤。
    ATR移动止损管理风险。

    参数:
        fast_ema_period: 快EMA周期 (默认: 20)
        slow_ema_period: 慢EMA周期 (默认: 50)
        vol_lookback: 波动率回顾周期 (默认: 20)
        vol_multiplier: 通道宽度倍数 (默认: 2.0)
        filter_ema_period: 方向过滤EMA周期 (默认: 200, 0=禁用)
        atr_period: ATR止损周期 (默认: 14)
        atr_stop_mult: ATR止损倍数 (默认: 3.0)
        fixed_size: 固定交易手数 (默认: 1)
        bar_interval_minutes: 合成K线周期分钟数 (默认: 60)
    """

    author: str = "CTA Agent"

    # ── 策略参数 ──────────────────────────────────────────
    fast_ema_period: int = 20
    slow_ema_period: int = 50
    vol_lookback: int = 20
    vol_multiplier: float = 2.0
    filter_ema_period: int = 200
    atr_period: int = 14
    atr_stop_mult: float = 3.0
    fixed_size: int = 1
    bar_interval_minutes: int = 60

    # ── 策略变量 ──────────────────────────────────────────
    baseline: float = 0.0
    upper_envelope: float = 0.0
    lower_envelope: float = 0.0
    regime: int = 0
    filter_ema: float = 0.0
    atr_value: float = 0.0
    stop_price: float = 0.0
    bars_in_trade: int = 0

    parameters: list[str] = [
        "fast_ema_period",
        "slow_ema_period",
        "vol_lookback",
        "vol_multiplier",
        "filter_ema_period",
        "atr_period",
        "atr_stop_mult",
        "fixed_size",
        "bar_interval_minutes",
    ]
    variables: list[str] = [
        "baseline",
        "upper_envelope",
        "lower_envelope",
        "regime",
        "filter_ema",
        "atr_value",
        "stop_price",
        "bars_in_trade",
    ]

    def __init__(self, cta_engine: Any, strategy_name: str,
                 vt_symbol: str, setting: dict[str, Any]) -> None:
        """初始化策略."""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg: BarGenerator = BarGenerator(
            self.on_bar, self.bar_interval_minutes, self.on_window_bar
        )
        self.am: ArrayManager = ArrayManager(max(self.fast_ema_period,
                                                  self.slow_ema_period,
                                                  self.vol_lookback,
                                                  self.filter_ema_period,
                                                  self.atr_period) + 10)

        # 自定义指标状态
        self._fast_alpha: float = 2.0 / (self.fast_ema_period + 1.0)
        self._slow_alpha: float = 2.0 / (self.slow_ema_period + 1.0)
        self._fast_ema_val: float = 0.0
        self._slow_ema_val: float = 0.0
        self._filter_ema_val: float = 0.0
        self._filter_alpha: float = (
            2.0 / (self.filter_ema_period + 1.0) if self.filter_ema_period > 0
            else 0.0
        )
        self._baseline_history: deque[float] = deque(maxlen=self.vol_lookback)

    def on_init(self) -> None:
        """策略初始化回调."""
        self.write_log("AlphaFlow v2 策略初始化")
        self.load_bar(10)

    def on_start(self) -> None:
        """策略启动回调."""
        self.write_log("AlphaFlow v2 策略启动")

    def on_stop(self) -> None:
        """策略停止回调."""
        self.write_log("AlphaFlow v2 策略停止")

    def on_tick(self, tick: TickData) -> None:
        """Tick推送回调."""
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        """1分钟K线回调."""
        self.bg.update_bar(bar)

    def on_window_bar(self, bar: BarData) -> None:
        """
        窗口K线回调 — 核心策略逻辑入口.
        """
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        self._update_indicators(bar)
        if len(self._baseline_history) < self.vol_lookback:
            self.put_event()
            return

        if self.pos == 0:
            self._handle_no_position(bar)
        elif self.pos > 0:
            self._handle_long_position(bar)

        self.put_event()

    # ── 指标计算 ──────────────────────────────────────────

    def _update_indicators(self, bar: BarData) -> None:
        """更新所有指标."""
        hlc3: float = (bar.high_price + bar.low_price + bar.close_price) / 3.0

        # 双EMA基线
        if self._fast_ema_val == 0.0:
            self._fast_ema_val = hlc3
            self._slow_ema_val = hlc3
            self._filter_ema_val = hlc3
        else:
            self._fast_ema_val = (
                self._fast_alpha * hlc3
                + (1.0 - self._fast_alpha) * self._fast_ema_val
            )
            self._slow_ema_val = (
                self._slow_alpha * hlc3
                + (1.0 - self._slow_alpha) * self._slow_ema_val
            )
            if self._filter_alpha > 0:
                self._filter_ema_val = (
                    self._filter_alpha * hlc3
                    + (1.0 - self._filter_alpha) * self._filter_ema_val
                )

        self.baseline = (self._fast_ema_val + self._slow_ema_val) / 2.0
        self.filter_ema = self._filter_ema_val

        # 波动率包络
        self._baseline_history.append(self.baseline)
        if len(self._baseline_history) >= self.vol_lookback:
            baseline_std: float = float(np.std(list(self._baseline_history)))
            self.upper_envelope = (
                self.baseline + self.vol_multiplier * baseline_std
            )
            self.lower_envelope = (
                self.baseline - self.vol_multiplier * baseline_std
            )

        self.atr_value = self.am.atr(self.atr_period)

    # ── 交易逻辑 ──────────────────────────────────────────

    def _is_bull_filter(self, bar: BarData) -> bool:
        """方向过滤：是否允许做多.

        filter_ema_period=0 时禁用过滤。
        """
        if self.filter_ema_period == 0:
            return True
        return bar.close_price > self.filter_ema

    def _handle_no_position(self, bar: BarData) -> None:
        """空仓入场逻辑."""
        prev_regime: int = self.regime

        if bar.close_price > self.upper_envelope:
            self.regime = 1
        elif bar.close_price < self.lower_envelope:
            self.regime = 0

        # 体制翻转 + 方向过滤
        if prev_regime == 0 and self.regime == 1:
            if self._is_bull_filter(bar):
                self.buy(bar.close_price, self.fixed_size)
                self.bars_in_trade = 0
                self.stop_price = 0.0

    def _handle_long_position(self, bar: BarData) -> None:
        """多头持仓管理."""
        self.bars_in_trade += 1

        # 体制退出
        if bar.close_price < self.lower_envelope:
            self.regime = 0
            self.sell(bar.close_price, abs(self.pos))
            return

        # 方向过滤退出
        if self.filter_ema_period > 0 and not self._is_bull_filter(bar):
            self.regime = 0
            self.sell(bar.close_price, abs(self.pos))
            return

        # ATR移动止损
        if self.atr_value > 0:
            new_stop: float = (
                bar.close_price - self.atr_stop_mult * self.atr_value
            )
            if new_stop > self.stop_price:
                self.stop_price = new_stop

            if bar.close_price <= self.stop_price and self.stop_price > 0:
                self.regime = 0
                self.sell(bar.close_price, abs(self.pos))
                return

    # ── 委托回调 ──────────────────────────────────────────

    def on_order(self, order: OrderData) -> None:
        """委托状态更新回调."""
        pass

    def on_trade(self, trade: TradeData) -> None:
        """成交回调."""
        self.put_event()

#!/usr/bin/env python3
"""AlphaFlow v2 — 波动率包络 + 动态仓位策略。

v2变更:
  - 增加filter_ema_period参数：只在长期EMA方向交易
  - 支持通过bar_interval_minutes自定义合成K线周期（默认60=1h）
  - 动态仓位：capital/ATR * multiplier
"""

from __future__ import annotations
from typing import Any
from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy_ctastrategy import CtaTemplate, BarGenerator, ArrayManager


class AlphaFlowStrategy(CtaTemplate):
    """Alpha Flow 波动率包络策略 v2."""

    author: str = "CTA Agent"

    fast_ema_period: int = 20
    slow_ema_period: int = 50
    vol_lookback: int = 20
    vol_multiplier: float = 3.0
    filter_ema_period: int = 0
    atr_period: int = 14
    atr_stop_mult: float = 3.0
    fixed_size: int = 1
    use_dynamic_size: bool = False
    position_multiplier: float = 0.005
    bar_interval_minutes: int = 60

    baseline: float = 0.0
    upper_envelope: float = 0.0
    lower_envelope: float = 0.0
    regime: int = 0
    filter_ema: float = 0.0
    atr_value: float = 0.0
    stop_price: float = 0.0
    bars_in_trade: int = 0

    parameters: list[str] = [
        "fast_ema_period", "slow_ema_period", "vol_lookback",
        "vol_multiplier", "filter_ema_period", "atr_period",
        "atr_stop_mult", "fixed_size", "use_dynamic_size",
        "position_multiplier", "bar_interval_minutes",
    ]
    variables: list[str] = [
        "baseline", "upper_envelope", "lower_envelope",
        "regime", "filter_ema", "atr_value", "stop_price", "bars_in_trade",
    ]

    def __init__(self, cta_engine: Any, strategy_name: str,
                 vt_symbol: str, setting: dict[str, Any]) -> None:
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)
        self.bg = BarGenerator(self.on_bar, self.bar_interval_minutes, self.on_window_bar)
        self.am = ArrayManager(max(self.fast_ema_period, self.slow_ema_period,
                                    self.vol_lookback, self.filter_ema_period,
                                    self.atr_period) + 10)
        self._fast_alpha = 2.0 / (self.fast_ema_period + 1.0)
        self._slow_alpha = 2.0 / (self.slow_ema_period + 1.0)
        self._fast_ema_val: float = 0.0
        self._slow_ema_val: float = 0.0
        self._filter_ema_val: float = 0.0
        self._filter_alpha = (2.0 / (self.filter_ema_period + 1.0)
                              if self.filter_ema_period > 0 else 0.0)

    def on_init(self) -> None:
        self.write_log("AlphaFlow v2 策略初始化")
        self.load_bar(10)

    def on_start(self) -> None:
        self.write_log("AlphaFlow v2 策略启动")

    def on_stop(self) -> None:
        self.write_log("AlphaFlow v2 策略停止")

    def on_tick(self, tick: TickData) -> None:
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        self.bg.update_bar(bar)

    def on_window_bar(self, bar: BarData) -> None:
        self.cancel_all()
        self.am.update_bar(bar)
        if not self.am.inited:
            return
        self._update_indicators(bar)
        if self.pos == 0:
            self._handle_no_position(bar)
        elif self.pos > 0:
            self._handle_long_position(bar)
        self.put_event()

    def _update_indicators(self, bar: BarData) -> None:
        hlc3 = (bar.high_price + bar.low_price + bar.close_price) / 3.0
        if self._fast_ema_val == 0.0:
            self._fast_ema_val = self._slow_ema_val = self._filter_ema_val = hlc3
        else:
            self._fast_ema_val = (self._fast_alpha * hlc3
                                  + (1.0 - self._fast_alpha) * self._fast_ema_val)
            self._slow_ema_val = (self._slow_alpha * hlc3
                                  + (1.0 - self._slow_alpha) * self._slow_ema_val)
            if self._filter_alpha > 0:
                self._filter_ema_val = (self._filter_alpha * hlc3
                                        + (1.0 - self._filter_alpha) * self._filter_ema_val)
        self.baseline = (self._fast_ema_val + self._slow_ema_val) / 2.0
        self.filter_ema = self._filter_ema_val
        self.atr_value = self.am.atr(self.atr_period)
        self.upper_envelope = self.baseline + self.vol_multiplier * self.atr_value
        self.lower_envelope = self.baseline - self.vol_multiplier * self.atr_value

    def _is_bull_filter(self, bar: BarData) -> bool:
        if self.filter_ema_period == 0:
            return True
        return bar.close_price > self.filter_ema

    def _get_size(self) -> int:
        if not self.use_dynamic_size:
            return self.fixed_size
        if self.atr_value <= 0:
            return 1
        capital: float = 200000.0
        dynamic: float = (capital / self.atr_value) * self.position_multiplier
        return max(1, int(dynamic))

    def _handle_no_position(self, bar: BarData) -> None:
        prev_regime = self.regime
        if bar.close_price > self.upper_envelope:
            self.regime = 1
        elif bar.close_price < self.lower_envelope:
            self.regime = 0
        if prev_regime == 0 and self.regime == 1:
            if self._is_bull_filter(bar):
                self.buy(bar.close_price, self._get_size())
                self.bars_in_trade = 0
                self.stop_price = 0.0

    def _handle_long_position(self, bar: BarData) -> None:
        self.bars_in_trade += 1
        if bar.close_price < self.lower_envelope:
            self.regime = 0
            self.sell(bar.close_price, abs(self.pos))
            return
        if self.filter_ema_period > 0 and not self._is_bull_filter(bar):
            self.regime = 0
            self.sell(bar.close_price, abs(self.pos))
            return
        if self.atr_value > 0:
            new_stop = bar.close_price - self.atr_stop_mult * self.atr_value
            if new_stop > self.stop_price:
                self.stop_price = new_stop
            if bar.close_price <= self.stop_price and self.stop_price > 0:
                self.regime = 0
                self.sell(bar.close_price, abs(self.pos))

    def on_order(self, order: OrderData) -> None:
        pass

    def on_trade(self, trade: TradeData) -> None:
        self.put_event()

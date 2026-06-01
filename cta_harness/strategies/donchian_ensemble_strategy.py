#!/usr/bin/env python3
"""Donchian 集成趋势跟踪策略（Catching Crypto Trends）。

基于 Concretum Group (2025) 论文的单标的实现。
核心机制:
  - 5个 Donchian close 通道集成信号（等权投票）
  - DonchianMid 单向追踪止损（仅上移，不下移）
  - 动态仓位（capital/ATR × multiplier）
  - 仅做多（长线比特币牛市优势）
"""

from __future__ import annotations

from datetime import time
from typing import Any

from vnpy.trader.object import BarData, TickData, OrderData, TradeData
from vnpy.trader.constant import Interval
from vnpy_ctastrategy import CtaTemplate, BarGenerator, ArrayManager


class DonchianEnsembleStrategy(CtaTemplate):
    """Donchian 集成趋势跟踪策略。

    日线 K线上运行：
    - 5 个 Donchian close 通道集成 → 入场信号
    - DonchianMid 单向追踪止损 → 离场
    - 动态仓位：capital/ATR × position_multiplier
    """

    author: str = "CTA Agent"

    # ── 策略参数 ──
    dc1: int = 5       # 最短 lookback
    dc2: int = 20
    dc3: int = 60
    dc4: int = 150
    dc5: int = 360      # 最长 lookback
    entry_threshold: float = 0.5  # 入场所需最小信号比例
    atr_period: int = 20
    position_multiplier: float = 0.005
    use_dynamic_size: bool = False
    fixed_size: int = 1

    # ── 策略变量 ──
    ensemble_signal: float = 0.0
    trail_stop: float = 0.0
    entry_price: float = 0.0
    atr_value: float = 0.0

    parameters: list[str] = [
        "dc1", "dc2", "dc3", "dc4", "dc5",
        "entry_threshold", "atr_period", "position_multiplier",
        "use_dynamic_size", "fixed_size",
    ]
    variables: list[str] = [
        "ensemble_signal", "trail_stop", "entry_price", "atr_value",
    ]

    # ── 内部状态 ──
    _donchian_highs: list[float]
    _donchian_mids: list[float]
    _lookbacks: list[int]

    def __init__(self, cta_engine: Any, strategy_name: str,
                 vt_symbol: str, setting: dict[str, Any]) -> None:
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        # 日线 BarGenerator（加密 24x7，UTC 午夜收盘）
        self.bg = BarGenerator(
            self.on_bar, 1, self.on_daily_bar, Interval.DAILY,
            daily_end=time(0, 0),
        )
        # ArrayManager 需要容纳最长 lookback + ATR + 余量
        self._lookbacks = [self.dc1, self.dc2, self.dc3, self.dc4, self.dc5]
        max_lookback: int = max(self._lookbacks)
        self.am = ArrayManager(max(max_lookback, self.atr_period) + 10)
        self._donchian_highs = [0.0] * len(self._lookbacks)
        self._donchian_mids = [0.0] * len(self._lookbacks)

    def on_init(self) -> None:
        self.write_log("DonchianEnsemble 策略初始化")
        self.load_bar(10)

    def on_start(self) -> None:
        self.write_log("DonchianEnsemble 策略启动")

    def on_stop(self) -> None:
        self.write_log("DonchianEnsemble 策略停止")

    def on_tick(self, tick: TickData) -> None:
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        self.bg.update_bar(bar)

    def on_daily_bar(self, bar: BarData) -> None:
        """日线 K线主逻辑（由 BarGenerator 触发）。"""
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
        """计算各 lookback 的 Donchian close 通道和 ensemble 信号。

        论文使用 close 而非 high/low 构建 Donchian 通道：
          DonchianUp_n = max(close[-n:], ..., close[-1])
          DonchianMid_n = (Up_n + Down_n) / 2

        排除当前 bar（索引 -1），否则 close >= DonchianUp 永远不成立。
        """
        am: ArrayManager = self.am
        closes = am.close

        for i, n in enumerate(self._lookbacks):
            window = closes[-(n + 1):-1]
            up: float = float(max(window))
            down: float = float(min(window))
            self._donchian_highs[i] = up
            self._donchian_mids[i] = (up + down) / 2.0

        # Ensemble 信号 = 各模型"突破"的等权平均
        current_close: float = closes[-1]
        active_count: int = sum(
            1 for i in range(len(self._lookbacks))
            if current_close >= self._donchian_highs[i]
        )
        self.ensemble_signal = active_count / len(self._lookbacks)
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
        """空仓时检测 ensemble 信号是否超过阈值。"""
        if self.ensemble_signal < self.entry_threshold:
            return

        size: int = self._get_size()
        price: float = bar.close_price
        self.buy(price, size)
        self.entry_price = price

        # 初始化追踪止损 = 当前所有模型 DonchianMid 的均值
        mids: list[float] = self._donchian_mids
        active_mids: list[float] = [
            mids[i] for i in range(len(self._lookbacks))
            if bar.close_price >= self._donchian_highs[i]
        ]
        if active_mids:
            self.trail_stop = sum(active_mids) / len(active_mids)
        else:
            # 极端情况：用最长 lookback 的 mid
            self.trail_stop = mids[-1]

    # ── 持仓管理 ──

    def _handle_long_position(self, bar: BarData) -> None:
        """持仓中：单向更新追踪止损，检测离场。

        论文的 trailing stop：TrailStop(t+1) = max{TrailStop(t), DonchianMid(t)}
        只在 DonchianMid 上移时更新，从不下移。
        """
        # 用最长 lookback (360) 的 DonchianMid 作为 trailing stop 锚点
        primary_mid: float = self._donchian_mids[-1]
        if primary_mid > self.trail_stop:
            self.trail_stop = primary_mid

        # 止损离场
        if bar.close_price <= self.trail_stop:
            self.sell(bar.close_price, abs(self.pos))

    # ── 委托/成交回调 ──

    def on_order(self, order: OrderData) -> None:
        pass

    def on_trade(self, trade: TradeData) -> None:
        self.put_event()

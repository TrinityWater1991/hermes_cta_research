"""
CCI 极端值趋势跟踪策略 (Unger Academy)

基于 Andrea Unger 的 CCI 趋势跟踪思路：
- CCI 突破 ±300 极端阈值入场（反直觉使用 CCI 作为趋势确认）
- CCI 回归零附近离场
- ATR 移动止损保护

原文在 COMEX Gold futures 上验证有效。
适配加密：1h K线、ATR 移动止损、双向交易。
"""

from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class CciExtremeTrendStrategy(CtaTemplate):
    """CCI 极端值趋势跟踪策略

    核心逻辑：
    1. 使用 BarGenerator 将 1m K线合成为 1h K线
    2. 在 1h K线上计算 CCI
    3. CCI 上穿 +entry_threshold 做多，下穿 -entry_threshold 做空
    4. CCI 回归至 exit_threshold 附近离场
    5. ATR 移动止损保护持仓
    """

    author = "CTA Research Pipeline (Unger Academy)"

    # 策略参数
    cci_window: int = 14
    entry_threshold: float = 300.0
    exit_threshold: float = 0.0
    atr_window: int = 14
    atr_multiplier: float = 3.0
    fixed_size: int = 1

    # 策略变量
    cci_value: float = 0.0
    atr_value: float = 0.0
    long_stop: float = 0.0
    short_stop: float = 0.0
    cci_prev: float = 0.0

    parameters: list[str] = [
        "cci_window",
        "entry_threshold",
        "exit_threshold",
        "atr_window",
        "atr_multiplier",
        "fixed_size",
    ]

    variables: list[str] = [
        "cci_value",
        "atr_value",
        "long_stop",
        "short_stop",
        "cci_prev",
    ]

    def __init__(
        self,
        cta_engine,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,
    ) -> None:
        """初始化策略实例"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        # 1分钟K线合成1小时K线
        self.bg = BarGenerator(self.on_bar, 60, self.on_hour_bar)
        self.am = ArrayManager()

        # 持仓期间追踪极端价，用于动态止损
        self.intra_trade_high: float = 0.0
        self.intra_trade_low: float = 0.0

    def on_init(self) -> None:
        """策略初始化回调"""
        self.write_log("CCI 极端值趋势跟踪策略初始化")
        self.load_bar(20)

    def on_start(self) -> None:
        """策略启动回调"""
        self.write_log("策略启动")

    def on_stop(self) -> None:
        """策略停止回调"""
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """Tick 更新回调"""
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        """1分钟 K线回调 —— 送入 BarGenerator 合成1小时"""
        self.bg.update_bar(bar)

    def on_hour_bar(self, bar: BarData) -> None:
        """1小时 K线回调 —— 主交易逻辑"""
        # 1. 撤销所有挂单
        self.cancel_all()

        # 2. 更新数据并计算指标
        self.am.update_bar(bar)
        if not self.am.inited:
            return

        self._calculate_indicators()

        # 3. 按持仓状态分发
        if self.pos == 0:
            self._handle_no_position(bar)
        elif self.pos > 0:
            self._handle_long_position(bar)
        elif self.pos < 0:
            self._handle_short_position(bar)

        # 4. 保存当前 CCI 为下一根的前值
        self.cci_prev = self.cci_value

        # 5. 推送状态更新
        self.put_event()

    def _calculate_indicators(self) -> None:
        """集中计算技术指标"""
        self.cci_value = self.am.cci(self.cci_window)
        self.atr_value = self.am.atr(self.atr_window)

    def _handle_no_position(self, bar: BarData) -> None:
        """空仓入场逻辑"""
        # CCI 上穿 +entry_threshold → 做多
        if (
            self.cci_value >= self.entry_threshold
            and self.cci_prev < self.entry_threshold
        ):
            self.buy(bar.close_price, self.fixed_size)
            self.intra_trade_high = bar.high_price
            self.write_log(f"CCI={self.cci_value:.1f} 上穿 +{self.entry_threshold}, 做多入场")

        # CCI 下穿 -entry_threshold → 做空
        elif (
            self.cci_value <= -self.entry_threshold
            and self.cci_prev > -self.entry_threshold
        ):
            self.short(bar.close_price, self.fixed_size)
            self.intra_trade_low = bar.low_price
            self.write_log(f"CCI={self.cci_value:.1f} 下穿 -{self.entry_threshold}, 做空入场")

    def _handle_long_position(self, bar: BarData) -> None:
        """多头持仓管理"""
        # 更新持仓期最高价
        self.intra_trade_high = max(self.intra_trade_high, bar.high_price)

        # CCI 下穿 exit_threshold → 离场
        if self.cci_value < self.exit_threshold:
            self.sell(bar.close_price, abs(self.pos))
            self.write_log(f"CCI={self.cci_value:.1f} 回归 {self.exit_threshold}, 多头离场")
            return

        # 更新 ATR 移动止损
        self.long_stop = self.intra_trade_high - self.atr_value * self.atr_multiplier
        self.sell(self.long_stop, abs(self.pos), True)

    def _handle_short_position(self, bar: BarData) -> None:
        """空头持仓管理"""
        # 更新持仓期最低价
        self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

        # CCI 上穿 -exit_threshold → 离场
        if self.cci_value > -self.exit_threshold:
            self.cover(bar.close_price, abs(self.pos))
            self.write_log(f"CCI={self.cci_value:.1f} 回归 -{self.exit_threshold}, 空头离场")
            return

        # 更新 ATR 移动止损
        self.short_stop = self.intra_trade_low + self.atr_value * self.atr_multiplier
        self.cover(self.short_stop, abs(self.pos), True)

    def on_order(self, order: OrderData) -> None:
        """委托回调"""
        pass

    def on_trade(self, trade: TradeData) -> None:
        """成交回调"""
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """停止单回调"""
        pass

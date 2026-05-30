"""
Kalman趋势指标策略（KalmanTrendStrategy）

基于Quantitativo "Fast Trend Following"文章的核心思路：
- 双Kalman滤波器（快线/慢线）跟踪价格
- 计算快线相对慢线的百分比偏离
- 偏离的滚动百分位数作为趋势强度指标（QTI）
- QTI超过阈值入场，回归离场
- ATR移动止损保护

适配：rb99.SHFE 15分钟K线
"""
from collections import deque

import numpy as np

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
from vnpy.trader.constant import Interval


class KalmanTrendStrategy(CtaTemplate):
    """
    双Kalman滤波器趋势跟踪策略。

    快线（低R）紧密跟踪价格，慢线（高R）平滑趋势。
    快线相对慢线的偏离百分位数作为趋势强度信号。
    """

    author: str = "cta_agent"

    # 策略参数
    bar_window: int = 15
    kalman_fast_r: float = 0.5
    kalman_slow_r: float = 50.0
    lookback_window: int = 200
    entry_threshold: int = 40
    exit_threshold: int = 0
    atr_window: int = 20
    atr_stop_multiplier: float = 2.0
    fixed_size: int = 1

    # 策略变量
    qti_value: float = 0.0
    atr_value: float = 0.0
    intra_trade_high: float = 0.0
    intra_trade_low: float = 0.0
    long_stop: float = 0.0
    short_stop: float = 0.0

    parameters: list[str] = [
        "bar_window",
        "kalman_fast_r",
        "kalman_slow_r",
        "lookback_window",
        "entry_threshold",
        "exit_threshold",
        "atr_window",
        "atr_stop_multiplier",
        "fixed_size",
    ]

    variables: list[str] = [
        "qti_value",
        "atr_value",
        "intra_trade_high",
        "intra_trade_low",
        "long_stop",
        "short_stop",
    ]

    def __init__(
        self,
        cta_engine: object,
        strategy_name: str,
        vt_symbol: str,
        setting: dict,
    ) -> None:
        """初始化策略。"""
        super().__init__(cta_engine, strategy_name, vt_symbol, setting)

        self.bg = BarGenerator(
            self.on_bar,
            window=self.bar_window,
            on_window_bar=self.on_window_bar,
        )
        self.am = ArrayManager(size=100)

        # Kalman滤波器状态
        self.fast_price: float = 0.0
        self.fast_trend: float = 0.0
        self.fast_p: np.ndarray = np.eye(2) * 1000.0

        self.slow_price: float = 0.0
        self.slow_trend: float = 0.0
        self.slow_p: np.ndarray = np.eye(2) * 1000.0

        # 偏离历史（用于计算百分位数）
        self.deviation_history: deque = deque(maxlen=2000)

        # 上一根K线的QTI值（用于判断穿越）
        self.prev_qti: float = 0.0

    def on_init(self) -> None:
        """策略初始化。"""
        self.write_log("策略初始化")
        self.load_bar(30)

    def on_start(self) -> None:
        """策略启动。"""
        self.write_log("策略启动")

    def on_stop(self) -> None:
        """策略停止。"""
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """Tick数据更新。"""
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        """1分钟K线更新。"""
        self.bg.update_bar(bar)

    def _kalman_update(
        self,
        price_est: float,
        trend_est: float,
        p_matrix: np.ndarray,
        measurement: float,
        r_noise: float,
    ) -> tuple[float, float, np.ndarray]:
        """
        单步Kalman滤波器更新。

        状态: [price, trend]
        转移: price_new = price + trend, trend_new = trend
        观测: z = price
        """
        # 预测步
        pred_price: float = price_est + trend_est
        pred_trend: float = trend_est

        # 状态转移矩阵 F
        f_matrix: np.ndarray = np.array([[1.0, 1.0], [0.0, 1.0]])
        # 过程噪声
        q_matrix: np.ndarray = np.array([[1.0, 0.0], [0.0, 1.0]]) * 0.01

        # 预测协方差
        p_pred: np.ndarray = f_matrix @ p_matrix @ f_matrix.T + q_matrix

        # 观测矩阵 H
        h_matrix: np.ndarray = np.array([[1.0, 0.0]])

        # 卡尔曼增益
        s: float = float(h_matrix @ p_pred @ h_matrix.T + r_noise)
        k_gain: np.ndarray = (p_pred @ h_matrix.T) / s

        # 更新步
        innovation: float = measurement - pred_price
        state: np.ndarray = np.array([[pred_price], [pred_trend]]) + k_gain * innovation
        p_new: np.ndarray = (np.eye(2) - k_gain @ h_matrix) @ p_pred

        return float(state[0, 0]), float(state[1, 0]), p_new

    def on_window_bar(self, bar: BarData) -> None:
        """合成K线更新，执行核心策略逻辑。"""
        self.cancel_all()

        self.am.update_bar(bar)
        if not self.am.inited:
            return

        # 更新双Kalman滤波器
        close: float = bar.close_price

        if self.fast_price == 0.0:
            # 首次初始化
            self.fast_price = close
            self.slow_price = close
            return

        self.fast_price, self.fast_trend, self.fast_p = self._kalman_update(
            self.fast_price, self.fast_trend, self.fast_p,
            close, self.kalman_fast_r,
        )
        self.slow_price, self.slow_trend, self.slow_p = self._kalman_update(
            self.slow_price, self.slow_trend, self.slow_p,
            close, self.kalman_slow_r,
        )

        # 计算快线相对慢线的百分比偏离
        if self.slow_price == 0.0:
            return
        deviation: float = (self.fast_price - self.slow_price) / self.slow_price * 100.0
        self.deviation_history.append(deviation)

        # 需要足够历史才能计算百分位
        if len(self.deviation_history) < self.lookback_window:
            return

        # 计算QTI：当前偏离在历史中的百分位（-100到+100）
        history_array: np.ndarray = np.array(self.deviation_history)
        recent: np.ndarray = history_array[-self.lookback_window:]
        percentile: float = float(np.sum(recent < deviation) / len(recent) * 200.0 - 100.0)

        self.prev_qti = self.qti_value
        self.qti_value = percentile

        # ATR
        self.atr_value = self.am.atr(self.atr_window)

        # 交易逻辑
        if self.pos == 0:
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = bar.low_price

            # QTI上穿entry_threshold做多
            if (self.qti_value > self.entry_threshold
                    and self.prev_qti <= self.entry_threshold):
                self.buy(bar.close_price, self.fixed_size)
            # QTI下穿-entry_threshold做空
            elif (self.qti_value < -self.entry_threshold
                  and self.prev_qti >= -self.entry_threshold):
                self.short(bar.close_price, self.fixed_size)

        elif self.pos > 0:
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.long_stop = (
                self.intra_trade_high - self.atr_value * self.atr_stop_multiplier
            )

            # QTI回归exit_threshold离场
            if self.qti_value < self.exit_threshold:
                self.sell(bar.close_price, abs(self.pos))
            else:
                self.sell(self.long_stop, abs(self.pos), stop=True)

        elif self.pos < 0:
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
            self.short_stop = (
                self.intra_trade_low + self.atr_value * self.atr_stop_multiplier
            )

            # QTI回归-exit_threshold离场
            if self.qti_value > -self.exit_threshold:
                self.cover(bar.close_price, abs(self.pos))
            else:
                self.cover(self.short_stop, abs(self.pos), stop=True)

        self.put_event()

    def on_order(self, order: OrderData) -> None:
        """委托更新。"""
        pass

    def on_trade(self, trade: TradeData) -> None:
        """成交更新。"""
        self.put_event()

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """停止单更新。"""
        pass

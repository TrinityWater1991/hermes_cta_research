"""
VeighNa策略关键词:
ATR指标, RSI指标, 波动率过滤, 趋势跟踪, 移动止损, 百分比止损,
波动率判断, 强弱指数, 动态止损, 技术指标组合, 无固定止盈,
震荡行情过滤, 趋势确认, 回撤控制, 反弹控制, 价格极值,
趋势持续性, 风险管理, 多指标组合, 相对强弱
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


class AtrRsiStrategy(CtaTemplate):
    """
    基于ATR和RSI指标的趋势跟踪交易策略


    策略逻辑:
    1. 开仓条件：ATR值大于其均线(确认足够波动率) + RSI指标突破阈值
       - RSI > 50+rsi_entry 开多
       - RSI < 50-rsi_entry 开空
    2. 止损方式：百分比移动止损
       - 多头：从最高点回撤指定百分比
       - 空头：从最低点反弹指定百分比
    3. 无固定止盈，完全依靠移动止损锁定利润


    特点:
    - 趋势跟踪型，适合有明显趋势的市场
    - 动态止损，能有效控制回撤
    - 结合波动率过滤，避免区间震荡行情


    策略核心执行流程:

    1. K线数据更新 (on_bar)
       |
    2. 更新技术指标 (calculate_indicators)
       |
    3. 检查是否有持仓
       |
       ├── 无持仓:
       |    └── 检查ATR趋势条件 (check_trend_by_atr)
       |         └── 满足条件: 根据RSI判断开仓方向 (check_entry_by_rsi)
       |
    4. 更新移动止损目标价 (update_trailing_target)
       |
    5. 计算移动止损距离 (calculate_trailing_distance)
       |
    6. 计算止损触发价格 (calculate_trailing_stop)
       |
    7. 发送移动止损委托 (send_trailing_order)
    """

    author: str = "VeighNa AI"

    # 策略参数
    atr_window: int = 8                     # ATR指标周期，影响ATR计算的K线数量，建议6-12
    atr_ma_window: int = 6                  # ATR均线周期，用于判断波动率大小，建议4-8
    rsi_window: int = 7                     # RSI指标周期，影响RSI灵敏度，建议6-14
    rsi_entry: int = 42                     # RSI开仓偏移值，与50基准相加减形成上下阈值，建议30-45
    trailing_percent: float = 0.5           # 移动止损百分比，相对于极值价格的回撤百分比，建议0.3-1.5
    fixed_size: int = 1                     # 固定交易数量，每次交易的合约数，建议根据资金量调整

    # 策略变量
    atr_value: float = 0.0                  # ATR指标值，当前周期的真实波动范围，用于判断市场波动状态
    atr_ma: float = 0.0                     # ATR均线值，多周期ATR的平均值，用作波动率过滤的基准线
    rsi_value: float = 0.0                  # RSI指标值，当前周期的相对强弱指数，用于判断市场多空方向
    rsi_long_threshold: float = 0.0         # RSI多头开仓阈值，RSI突破此值时开多，等于50+rsi_entry
    rsi_short_threshold: float = 0.0        # RSI空头开仓阈值，RSI跌破此值时开空，等于50-rsi_entry
    long_trailing_target: float = 0.0       # 多头移动目标价，多头持仓期间的最高价，用于计算移动止损点
    short_trailing_target: float = 0.0      # 空头移动目标价，空头持仓期间的最低价，用于计算移动止损点
    long_trailing_distance: float = 0.0     # 多头移动距离，从最高价回撤的距离，等于最高价乘以回撤百分比
    short_trailing_distance: float = 0.0    # 空头移动距离，从最低价反弹的距离，等于最低价乘以回撤百分比
    long_trailing_stop: float = 0.0         # 多头移动止损价，触发平多仓的价格，等于最高价减去移动距离
    short_trailing_stop: float = 0.0        # 空头移动止损价，触发平空仓的价格，等于最低价加上移动距离

    # 参数名称列表
    parameters: list[str] = [
        "atr_window",
        "atr_ma_window",
        "rsi_window",
        "rsi_entry",
        "trailing_percent",
        "fixed_size"
    ]

    # 变量名称列表
    variables: list[str] = [
        "atr_value",
        "atr_ma",
        "rsi_value",
        "rsi_long_threshold",
        "rsi_short_threshold",
        "long_trailing_target",
        "short_trailing_target",
        "long_trailing_distance",
        "short_trailing_distance",
        "long_trailing_stop",
        "short_trailing_stop"
    ]

    def on_init(self) -> None:
        """
        策略初始化回调

        作用:
            在策略启动时执行一次，用于初始化策略所需的变量和组件

        执行流程:
            1. 创建K线生成器和数组管理器
            2. 计算RSI开仓阈值
            3. 加载历史K线数据
        """
        self.write_log("策略初始化")

        self.bg: BarGenerator = BarGenerator(self.on_bar)
        self.am: ArrayManager = ArrayManager()

        self.rsi_long_threshold: int = 50 + self.rsi_entry
        self.rsi_short_threshold: int = 50 - self.rsi_entry

        self.load_bar(10)

    def on_start(self) -> None:
        """
        策略启动回调

        作用:
            在交易引擎启动策略时调用一次
        """
        self.write_log("策略启动")

    def on_stop(self) -> None:
        """
        策略停止回调

        作用:
            在交易引擎停止策略时调用一次
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """
        新的Tick数据更新回调

        作用:
            处理最新的市场Tick数据

        参数:
            tick (TickData): 最新的市场Tick数据对象

        执行逻辑:
            将Tick数据传入K线生成器，生成K线数据
        """
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        """
        新的Bar数据更新回调

        作用:
            处理最新的K线数据，执行策略核心逻辑

        参数:
            bar (BarData): 最新的K线数据对象

        执行流程:
            1. 更新K线数据到数组管理器并检查初始化
            2. 撤销之前的所有挂单
            3. 计算技术指标ATR和RSI
            4. 判断是否有开仓机会
            5. 更新移动止损参数
            6. 执行移动止损策略
            7. 推送策略状态更新
        """
        # 更新K线缓存数组并检查初始化完成
        if not self.update_am(bar):
            return

        # 撤销之前的所有委托
        self.cancel_all()

        # 计算ATR和RSI指标值
        self.calculate_indicators()

        # 如果没有持仓,判断是否开仓
        if not self.pos:
            # 判断ATR趋势是否满足开仓条件
            if self.check_trend_by_atr():
                # 根据RSI指标值判断开仓方向
                self.check_entry_by_rsi(bar)

        # 更新移动止损的目标价格
        self.update_trailing_target(bar)

        # 计算移动止损的距离
        self.calculate_trailing_distance()

        # 计算移动止损的触发价格
        self.calculate_trailing_stop()

        # 发送移动止损委托
        self.send_trailing_order()

        # 推送策略状态更新事件
        self.put_event()

    def update_am(self, bar: BarData) -> bool:
        """
        更新K线到数据容器

        作用:
            将最新K线数据添加到数组管理器并检查是否已完成初始化

        参数:
            bar (BarData): 当前K线数据对象

        返回:
            bool: True表示K线缓存容器中的数据长度已初始化完成，False表示尚未完成初始化
        """
        self.am.update_bar(bar)
        return self.am.inited

    def calculate_indicators(self) -> None:
        """
        计算相关技术指标

        作用:
            计算策略所需的ATR和RSI技术指标值

        执行逻辑:
            1. 计算ATR值和ATR均线值
            2. 计算RSI值
        """
        atr_array = self.am.atr(self.atr_window, array=True)
        self.atr_value = atr_array[-1]
        self.atr_ma = atr_array[-self.atr_ma_window:].mean()

        self.rsi_value = self.am.rsi(self.rsi_window)

    def check_trend_by_atr(self) -> bool:
        """
        基于ATR指标判断市场趋势强度

        原理:
            当ATR值大于其移动平均时，表示市场波动加剧，
            适合趋势交易；反之表示市场波动较小，不适合入场

        返回:
            bool: True表示波动率足够，可以考虑入场；False表示波动率不足
        """
        return self.atr_value > self.atr_ma

    def check_entry_by_rsi(self, bar: BarData) -> None:
        """
        基于RSI指标判断多空方向并执行开仓

        原理:
            RSI指标在50以上为多头市场，50以下为空头市场
            当RSI突破上下阈值时，表示趋势形成的可能性较大

        参数:
            bar (BarData): 当前K线数据对象

        执行逻辑:
            RSI > 50+rsi_entry: 开多单(价格+5滑点)
            RSI < 50-rsi_entry: 开空单(价格-5滑点)
        """
        if self.rsi_value > self.rsi_long_threshold:
            self.buy(bar.close_price + 5, self.fixed_size)
        elif self.rsi_value < self.rsi_short_threshold:
            self.short(bar.close_price - 5, self.fixed_size)

    def update_trailing_target(self, bar: BarData) -> None:
        """
        更新移动止损跟踪目标价

        作用:
            根据持仓方向和当前K线价格，更新移动止损的目标价格

        参数:
            bar (BarData): 当前K线数据对象

        执行逻辑:
            1. 无持仓时，记录当前高低点
            2. 多头持仓时，持续更新最高价作为目标
            3. 空头持仓时，持续更新最低价作为目标
        """
        if self.pos == 0:
            self.long_trailing_target = bar.high_price
            self.short_trailing_target = bar.low_price
        elif self.pos > 0:
            self.long_trailing_target = max(self.long_trailing_target, bar.high_price)
            self.short_trailing_target = bar.low_price
        elif self.pos < 0:
            self.short_trailing_target = min(self.short_trailing_target, bar.low_price)
            self.long_trailing_target = bar.high_price

    def calculate_trailing_distance(self) -> None:
        """
        计算移动止损距离

        作用:
            根据持仓方向和移动止损百分比，计算移动止损的具体点数距离

        执行逻辑:
            1. 多头持仓时，计算从高点回撤的距离
            2. 空头持仓时，计算从低点反弹的距离
            3. 距离等于目标价格乘以移动止损百分比
        """
        if self.pos > 0:
            self.long_trailing_distance = self.long_trailing_target * self.trailing_percent / 100
            self.short_trailing_distance = 0
        elif self.pos < 0:
            self.long_trailing_distance = 0
            self.short_trailing_distance = self.short_trailing_target * self.trailing_percent / 100

    def calculate_trailing_stop(self) -> None:
        """
        计算移动止损价格

        作用:
            根据目标价格和止损距离，计算具体的止损触发价格

        执行逻辑:
            1. 多头持仓时，止损价 = 最高价 - 止损距离
            2. 空头持仓时，止损价 = 最低价 + 止损距离
        """
        if self.pos > 0:
            self.long_trailing_stop = self.long_trailing_target - self.long_trailing_distance
            self.short_trailing_stop = 0
        elif self.pos < 0:
            self.long_trailing_stop = 0
            self.short_trailing_stop = self.short_trailing_target + self.short_trailing_distance

    def send_trailing_order(self) -> None:
        """
        发送移动止损委托

        作用:
            根据计算的止损价格，发送对应的止损委托单

        执行逻辑:
            1. 多头持仓时，发送卖出止损单(止损价格触发时平仓)
            2. 空头持仓时，发送买入止损单(止损价格触发时平仓)
        """
        if self.pos > 0:
            self.sell(self.long_trailing_stop, abs(self.pos), stop=True)
        elif self.pos < 0:
            self.cover(self.short_trailing_stop, abs(self.pos), stop=True)

    def on_order(self, order: OrderData) -> None:
        """
        新的订单数据更新回调

        作用:
            处理委托单状态更新事件
            用于跟踪订单状态、分析成交情况等

        参数:
            order (OrderData): 委托订单数据对象
        """
        pass

    def on_trade(self, trade: TradeData) -> None:
        """
        新的成交数据更新回调

        作用:
            处理成交回报事件
            记录交易状态、更新持仓信息、发送通知等

        参数:
            trade (TradeData): 成交数据对象

        执行逻辑:
            更新策略UI界面
        """
        pass

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """
        停止单更新回调

        作用:
            处理本地停止单状态变化事件
            用于跟踪停止单触发、撤销等状态

        参数:
            stop_order (StopOrder): 本地停止单数据对象
        """
        pass

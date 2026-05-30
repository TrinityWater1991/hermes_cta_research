"""
VeighNa策略关键词:
布林通道, 通道突破, CCI指标, 趋势过滤, 动态止损, ATR止损, 移动止损,
技术指标, 趋势跟踪, 突破策略, 通道交易, 多级别, 15分钟周期,
波动率指标, 趋势确认, 价格通道, 指标组合, 资金管理, 风险控制
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


class BollChannelStrategy(CtaTemplate):
    """
    基于布林通道(Bollinger Bands)和CCI指标的交易策略


    策略逻辑:
    1. 根据CCI指标判断市场方向
       - CCI > 0 做多：以布林带上轨做多
       - CCI < 0 做空：以布林带下轨做空
    2. 止损方式：ATR倍数移动止损
       - 多头：最高价减去ATR乘数
       - 空头：最低价加上ATR乘数
    3. 使用15分钟周期K线计算指标


    特点:
    - 结合趋势和通道突破思想
    - 基于ATR值的动态止损
    - 通过CCI过滤趋势方向


    策略核心执行流程:

    1. K线数据更新 (on_bar → on_15min_bar)
       |
    2. 更新技术指标 (calculate_indicators)
       |
    3. 检查是否有持仓
       |
       ├── 无持仓:
       |    └── 根据CCI判断开仓方向 (check_signal_by_cci)
       |
       ├── 持有多头/空头:
       |    ├── 更新价格水平 (update_price_levels)
       |    ├── 计算止损价格 (calculate_stop_price)
       |    └── 发送止损订单 (send_stop_orders)
    """

    author: str = "用Python的交易员"

    # 策略参数
    boll_window: int = 18                   # 布林带窗口期，影响布林带宽度和灵敏度
    boll_dev: float = 3.4                   # 布林带标准差倍数，影响通道宽度，越大通道越宽
    cci_window: int = 10                    # CCI指标周期，影响CCI计算的K线数量
    atr_window: int = 30                    # ATR指标周期，用于计算动态止损距离
    sl_multiplier: float = 5.2              # 止损倍数，ATR值乘以此倍数得到止损距离
    fixed_size: int = 1                     # 固定交易数量，每次交易的合约数

    # 策略变量
    boll_up: float = 0                      # 布林带上轨，突破时开多的价格位置
    boll_down: float = 0                    # 布林带下轨，突破时开空的价格位置
    cci_value: float = 0                    # CCI指标值，判断市场趋势方向
    atr_value: float = 0                    # ATR指标值，测量市场波动性，用于计算止损

    intra_trade_high: float = 0             # 持仓期间的最高价，用于多头移动止损点计算
    intra_trade_low: float = 0              # 持仓期间的最低价，用于空头移动止损点计算
    long_stop: float = 0                    # 多头止损价格，触发平多仓的价格
    short_stop: float = 0                   # 空头止损价格，触发平空仓的价格

    parameters: list[str] = [
        "boll_window",
        "boll_dev",
        "cci_window",
        "atr_window",
        "sl_multiplier",
        "fixed_size"
    ]
    variables: list[str] = [
        "boll_up",
        "boll_down",
        "cci_value",
        "atr_value",
        "intra_trade_high",
        "intra_trade_low",
        "long_stop",
        "short_stop"
    ]

    def on_init(self) -> None:
        """
        策略初始化回调

        作用:
            在策略启动时执行一次，用于初始化策略所需的变量和组件

        执行流程:
            1. 创建K线生成器和数组管理器
            2. 加载历史K线数据
        """
        self.write_log("策略初始化")

        # 创建K线生成器和指标计算器
        self.bg = BarGenerator(self.on_bar, 15, self.on_15min_bar)
        self.am = ArrayManager()

        # 加载历史数据用于初始化指标计算
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
            处理最新的K线数据

        参数:
            bar (BarData): 最新的K线数据对象

        执行逻辑:
            将K线数据传入K线生成器，合成更大时间周期的K线
        """
        self.bg.update_bar(bar)

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
        am = self.am
        am.update_bar(bar)
        return am.inited

    def calculate_indicators(self) -> None:
        """
        计算相关技术指标

        作用:
            计算策略所需的布林带、CCI和ATR技术指标值

        执行逻辑:
            1. 计算布林带上下轨
            2. 计算CCI指标值
            3. 计算ATR值
        """
        self.boll_up, self.boll_down = self.am.boll(self.boll_window, self.boll_dev)
        self.cci_value = self.am.cci(self.cci_window)
        self.atr_value = self.am.atr(self.atr_window)

    def check_signal_by_cci(self, bar: BarData) -> None:
        """
        基于CCI指标判断多空方向并执行开仓

        原理:
            CCI指标在0以上为多头市场，0以下为空头市场
            多头市场在布林上轨开多，空头市场在布林下轨开空

        参数:
            bar (BarData): 当前K线数据对象

        执行逻辑:
            1. 初始化区间最高价和最低价
            2. CCI > 0: 在布林带上轨开多单
            3. CCI < 0: 在布林带下轨开空单
        """
        # 初始化区间最高/最低价
        self.intra_trade_high = bar.high_price
        self.intra_trade_low = bar.low_price

        # 基于CCI指标值判断开仓方向
        if self.cci_value > 0:
            self.buy(self.boll_up, self.fixed_size, True)
        elif self.cci_value < 0:
            self.short(self.boll_down, self.fixed_size, True)

    def update_price_levels(self, bar: BarData) -> None:
        """
        更新价格水平

        作用:
            根据持仓方向和当前K线价格，更新跟踪的最高价和最低价

        参数:
            bar (BarData): 当前K线数据对象

        执行逻辑:
            1. 多头持仓时，更新最高价(取最大值)和记录当前最低价
            2. 空头持仓时，更新最低价(取最小值)和记录当前最高价
        """
        if self.pos > 0:
            # 更新多头持仓的最高价和最低价
            self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
            self.intra_trade_low = bar.low_price
        elif self.pos < 0:
            # 更新空头持仓的最高价和最低价
            self.intra_trade_high = bar.high_price
            self.intra_trade_low = min(self.intra_trade_low, bar.low_price)

    def calculate_stop_price(self) -> None:
        """
        计算止损价格

        作用:
            根据跟踪的极值价格和ATR值，计算移动止损的触发价格

        原理:
            使用ATR的倍数作为止损距离，随着价格变动自动调整止损位置

        执行逻辑:
            1. 多头持仓时，止损价 = 最高价 - (ATR值 * 倍数)
            2. 空头持仓时，止损价 = 最低价 + (ATR值 * 倍数)
        """
        if self.pos > 0:
            # 计算多头移动止损价格
            self.long_stop = self.intra_trade_high - self.atr_value * self.sl_multiplier
        elif self.pos < 0:
            # 计算空头移动止损价格
            self.short_stop = self.intra_trade_low + self.atr_value * self.sl_multiplier

    def send_stop_orders(self) -> None:
        """
        发送止损委托

        作用:
            根据计算的止损价格，发送对应的止损委托单

        执行逻辑:
            1. 多头持仓时，发送卖出止损单(止损价格触发时平仓)
            2. 空头持仓时，发送买入止损单(止损价格触发时平仓)
        """
        if self.pos > 0:
            # 发送多头止损委托
            self.sell(self.long_stop, abs(self.pos), True)
        elif self.pos < 0:
            # 发送空头止损委托
            self.cover(self.short_stop, abs(self.pos), True)

    def on_15min_bar(self, bar: BarData) -> None:
        """
        15分钟K线数据更新回调

        作用:
            处理合成的15分钟K线数据，执行策略核心逻辑

        参数:
            bar (BarData): 15分钟周期的K线数据对象

        执行流程:
            1. 撤销所有未成交委托
            2. 更新K线数据并检查初始化状态
            3. 计算技术指标
            4. 根据持仓状态执行不同逻辑:
               - 无持仓: 检查CCI信号并开仓
               - 有持仓: 更新价格水平、计算止损价格、发送止损委托
            5. 更新图形界面显示
        """
        # 撤销所有未成交委托
        self.cancel_all()

        # 更新K线数据到指标计算器并检查初始化状态
        if not self.update_am(bar):
            return

        # 计算技术指标
        self.calculate_indicators()

        # 根据持仓情况执行不同的交易逻辑
        if self.pos == 0:
            # 无持仓状态，检查开仓信号
            self.check_signal_by_cci(bar)
        else:
            # 有持仓状态，更新价格水平
            self.update_price_levels(bar)

            # 计算止损价格
            self.calculate_stop_price()

            # 发送止损委托
            self.send_stop_orders()

        # 更新图形界面显示
        self.put_event()

    def on_order(self, order: OrderData) -> None:
        """
        委托状态更新回调

        作用:
            当委托状态发生变化时调用，处理委托相关的后续操作

        参数:
            order (OrderData): 委托单对象
        """
        pass

    def on_trade(self, trade: TradeData) -> None:
        """
        成交回报更新回调

        作用:
            当有新的成交发生时调用，处理成交相关的后续操作

        参数:
            trade (TradeData): 成交数据对象
        """
        pass

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """
        停止单状态更新回调

        作用:
            当本地停止单状态发生变化时调用，处理停止单相关的后续操作

        参数:
            stop_order (StopOrder): 停止单对象
        """
        pass

"""
VeighNa策略关键词:
海龟交易法则, 唐奇安通道, 突破策略, 趋势跟踪, 分批加仓, 金字塔加仓,
风险管理, ATR止损, 波动率止损, 多周期通道, 周期优化, 突破入场,
反向突破离场, N日高点突破, N日低点突破, 大波动行情, 高低点计算,
趋势交易系统, 资金管理, 加仓逻辑
"""

from vnpy_ctastrategy import (
    CtaTemplate,
    StopOrder,
    Direction,
    TickData,
    BarData,
    TradeData,
    OrderData,
    BarGenerator,
    ArrayManager,
)


class TurtleSignalStrategy(CtaTemplate):
    """
    海龟信号交易策略

    策略逻辑:
    1. 入场信号: 通过唐奇安通道(Donchian Channel)判断
       - 价格突破N日高点开多
       - 价格跌破N日低点开空
    2. 出场信号: 通过较短周期的唐奇安通道反向突破离场
    3. 止损方式: 基于ATR的固定风险止损
       - 多头: 按照2倍ATR设置止损
       - 空头: 按照2倍ATR设置止损
    4. 加仓机制: 按照ATR间隔的价格分批加仓

    特点:
    - 趋势跟踪型，适合大波动行情
    - ATR动态止损，控制每次交易风险
    - 金字塔式分批加仓，降低整体持仓成本

    策略核心执行流程:

    1. K线数据更新 (on_bar)
       |
    2. 判断是否有持仓
       |
       ├── 无持仓:
       |    └── 计算入场通道上下轨
       |         └── 突破上轨开多，突破下轨开空
       |
       ├── 多头持仓:
       |    ├── 继续检测上轨突破加仓
       |    └── 检测出场通道下轨或止损价平仓
       |
       └── 空头持仓:
            ├── 继续检测下轨突破加仓
            └── 检测出场通道上轨或止损价平仓
    """
    author: str = "VeighNa AI"

    # 策略参数
    entry_window: int = 20                # 入场通道周期，计算唐奇安通道的周期数，建议20-55
    exit_window: int = 10                 # 出场通道周期，计算唐奇安通道的周期数，建议10-20
    atr_window: int = 20                  # ATR周期，计算真实波动幅度的周期数，建议14-20
    fixed_size: int = 1                   # 固定交易数量，每次交易的合约数，建议根据资金量调整

    # 策略变量
    entry_up: float = 0                   # 入场通道上轨，最近N日最高价，用于做多信号
    entry_down: float = 0                 # 入场通道下轨，最近N日最低价，用于做空信号
    exit_up: float = 0                    # 出场通道上轨，最近M日最高价，用于空头离场信号
    exit_down: float = 0                  # 出场通道下轨，最近M日最低价，用于多头离场信号
    atr_value: float = 0                  # ATR指标值，衡量市场波动率，用于计算止损和加仓距离
    long_entry: float = 0                 # 多头入场价格，记录开仓价格用于计算止损
    short_entry: float = 0                # 空头入场价格，记录开仓价格用于计算止损
    long_stop: float = 0                  # 多头止损价格，基于ATR设置的动态止损价格
    short_stop: float = 0                 # 空头止损价格，基于ATR设置的动态止损价格

    # 参数名称列表
    parameters: list[str] = [
        "entry_window",
        "exit_window",
        "atr_window",
        "fixed_size"
    ]

    # 变量名称列表
    variables: list[str] = [
        "entry_up",
        "entry_down",
        "exit_up",
        "exit_down",
        "atr_value",
        "long_entry",
        "short_entry",
        "long_stop",
        "short_stop"
    ]

    def on_init(self) -> None:
        """
        策略初始化回调

        作用:
            在策略启动时执行一次，用于初始化策略所需的变量和组件
            设置K线合成器和数据管理器
            加载历史数据用于技术指标计算

        执行流程:
            1. 输出初始化日志
            2. 创建K线生成器和数组管理器对象
            3. 加载历史K线数据
        """
        # 输出初始化日志
        self.write_log("策略初始化")

        # 创建K线合成器对象，负责合成1分钟K线
        self.bg: BarGenerator = BarGenerator(self.on_bar)
        # 创建数组管理器，缓存K线数据用于计算指标
        self.am: ArrayManager = ArrayManager()

        # 加载历史数据，用于初始化技术指标
        self.load_bar(20)

    def on_start(self) -> None:
        """
        策略启动回调

        作用:
            在交易引擎启动策略时调用一次
            用于发送策略已启动的日志信息

        执行流程:
            1. 输出策略启动日志
        """
        # 输出策略启动日志
        self.write_log("策略启动")

    def on_stop(self) -> None:
        """
        策略停止回调

        作用:
            在交易引擎停止策略时调用一次
            用于发送策略已停止的日志信息

        执行流程:
            1. 输出策略停止日志
        """
        # 输出策略停止日志
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """
        新的Tick数据更新回调

        作用:
            处理最新的市场Tick数据
            将Tick数据传入K线生成器

        参数:
            tick (TickData): 最新的市场Tick数据对象

        执行流程:
            1. 将Tick数据传入K线合成器，生成K线数据
        """
        # 将TICK数据推送给K线合成器
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        """
        新的Bar数据更新回调

        作用:
            处理最新的K线数据，执行策略核心逻辑
            计算技术指标，检查开仓、加仓和平仓条件

        参数:
            bar (BarData): 最新的K线数据对象

        执行流程:
            1. 撤销之前的所有挂单
            2. 更新K线数据到数组管理器并检查初始化状态
            3. 计算唐奇安通道上下轨
            4. 根据持仓情况执行不同逻辑:
               - 无持仓: 计算ATR值，重置入场和止损价格，发送开仓委托
               - 有多头持仓: 检查新的加仓机会，设置止损或离场条件
               - 有空头持仓: 检查新的加仓机会，设置止损或离场条件
            5. 推送策略状态更新
        """
        # 撤销之前发出的所有未成交委托
        self.cancel_all()

        # 将K线数据更新到数组管理器中
        self.am.update_bar(bar)
        # 如果数据量不足，直接返回，不执行后续逻辑
        if not self.am.inited:
            return

        # 仅在无持仓时计算新的入场通道
        if not self.pos:
            # 计算唐奇安通道上下轨，作为开仓信号
            self.entry_up, self.entry_down = self.am.donchian(
                self.entry_window
            )

        # 计算出场通道上下轨，作为离场信号
        self.exit_up, self.exit_down = self.am.donchian(self.exit_window)

        if not self.pos:
            # 计算ATR值，用于动态止损和加仓间隔
            self.atr_value = self.am.atr(self.atr_window)

            # 重置开仓价格和止损价格
            self.long_entry = 0
            self.short_entry = 0
            self.long_stop = 0
            self.short_stop = 0

            # 发送多头和空头的开仓委托
            self.send_buy_orders(self.entry_up)
            self.send_short_orders(self.entry_down)
        elif self.pos > 0:
            # 持有多头仓位时，继续检查新的做多机会
            self.send_buy_orders(self.entry_up)

            # 设置平仓价格为止损价与出场通道下轨的较大值
            sell_price = max(self.long_stop, self.exit_down)
            # 发送平多仓委托
            self.sell(sell_price, abs(self.pos), True)

        elif self.pos < 0:
            # 持有空头仓位时，继续检查新的做空机会
            self.send_short_orders(self.entry_down)

            # 设置平仓价格为止损价与出场通道上轨的较小值
            cover_price = min(self.short_stop, self.exit_up)
            # 发送平空仓委托
            self.cover(cover_price, abs(self.pos), True)

        # 推送策略数据更新事件
        self.put_event()

    def on_trade(self, trade: TradeData) -> None:
        """
        新的成交数据更新回调

        作用:
            处理成交回报事件
            根据成交方向更新开仓价格和止损价格

        参数:
            trade (TradeData): 成交数据对象

        执行流程:
            1. 识别成交方向(多/空)
            2. 更新对应的入场价格记录
            3. 基于ATR值计算新的止损价格:
               - 多头: 入场价格减去2倍ATR
               - 空头: 入场价格加上2倍ATR
        """
        if trade.direction == Direction.LONG:
            # 多头成交，记录开仓价格
            self.long_entry = trade.price
            # 设置多头止损价格，基于ATR的固定风险模型
            self.long_stop = self.long_entry - 2 * self.atr_value
        else:
            # 空头成交，记录开仓价格
            self.short_entry = trade.price
            # 设置空头止损价格，基于ATR的固定风险模型
            self.short_stop = self.short_entry + 2 * self.atr_value

    def on_order(self, order: OrderData) -> None:
        """
        新的订单数据更新回调

        作用:
            处理委托单状态更新事件
            用于跟踪订单状态、分析成交情况等

        参数:
            order (OrderData): 委托订单数据对象

        执行流程:
            1. 当前实现为空，可根据需要扩展订单状态处理逻辑
        """
        # 当前版本不需要订单状态处理，留空
        pass

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """
        停止单更新回调

        作用:
            处理本地停止单状态变化事件
            用于跟踪停止单触发、撤销等状态

        参数:
            stop_order (StopOrder): 本地停止单数据对象

        执行流程:
            1. 当前实现为空，可根据需要扩展停止单状态处理逻辑
        """
        # 当前版本不需要停止单状态处理，留空
        pass

    def send_buy_orders(self, price: float) -> None:
        """
        发送多头委托

        作用:
            基于海龟交易系统的金字塔加仓法则发送多头委托
            通过ATR设置不同价位的加仓点

        参数:
            price (float): 多头入场基准价格

        执行流程:
            1. 计算当前持仓单位数
            2. 根据持仓单位数判断是否需要加仓:
               - 第一单位: 以基准价格直接开仓
               - 第二单位: 以基准价格+0.5ATR开仓
               - 第三单位: 以基准价格+1.0ATR开仓
               - 第四单位: 以基准价格+1.5ATR开仓
            3. 发送相应的买入停止单
        """
        # 计算当前持仓的单位数，用于判断加仓级别
        t = self.pos / self.fixed_size

        # 第一单位仓位，以突破价直接开仓
        if t < 1:
            # 发送买入停止单，以突破价开仓
            self.buy(price, self.fixed_size, True)

        # 第二单位仓位，以突破价+0.5ATR开仓
        if t < 2:
            # 发送买入停止单，价格上移0.5个ATR
            self.buy(price + self.atr_value * 0.5, self.fixed_size, True)

        # 第三单位仓位，以突破价+1.0ATR开仓
        if t < 3:
            # 发送买入停止单，价格上移1.0个ATR
            self.buy(price + self.atr_value, self.fixed_size, True)

        # 第四单位仓位，以突破价+1.5ATR开仓
        if t < 4:
            # 发送买入停止单，价格上移1.5个ATR
            self.buy(price + self.atr_value * 1.5, self.fixed_size, True)

    def send_short_orders(self, price: float) -> None:
        """
        发送空头委托

        作用:
            基于海龟交易系统的金字塔加仓法则发送空头委托
            通过ATR设置不同价位的加仓点

        参数:
            price (float): 空头入场基准价格

        执行流程:
            1. 计算当前持仓单位数
            2. 根据持仓单位数判断是否需要加仓:
               - 第一单位: 以基准价格直接开仓
               - 第二单位: 以基准价格-0.5ATR开仓
               - 第三单位: 以基准价格-1.0ATR开仓
               - 第四单位: 以基准价格-1.5ATR开仓
            3. 发送相应的卖出停止单
        """
        # 计算当前持仓的单位数，用于判断加仓级别
        t = self.pos / self.fixed_size

        # 第一单位仓位，以突破价直接开仓
        if t > -1:
            # 发送卖出停止单，以突破价开仓
            self.short(price, self.fixed_size, True)

        # 第二单位仓位，以突破价-0.5ATR开仓
        if t > -2:
            # 发送卖出停止单，价格下移0.5个ATR
            self.short(price - self.atr_value * 0.5, self.fixed_size, True)

        # 第三单位仓位，以突破价-1.0ATR开仓
        if t > -3:
            # 发送卖出停止单，价格下移1.0个ATR
            self.short(price - self.atr_value, self.fixed_size, True)

        # 第四单位仓位，以突破价-1.5ATR开仓
        if t > -4:
            # 发送卖出停止单，价格下移1.5个ATR
            self.short(price - self.atr_value * 1.5, self.fixed_size, True)

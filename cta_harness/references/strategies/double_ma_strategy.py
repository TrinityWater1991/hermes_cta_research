"""
VeighNa策略关键词:
双均线, 均线交叉, 趋势跟踪, 交叉信号, 小时级别, 多空转换,
动量策略, 经典策略, 趋势交易, 技术分析, 移动平均线,
短期均线, 长期均线, 金叉买入, 死叉卖出, 趋势确认,
震荡市场, 历史验证, 简单有效, 参数优化
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

from vnpy.trader.constant import Interval


class DoubleMaStrategy(CtaTemplate):
    """
    基于双均线交叉的趋势跟踪策略


    策略逻辑:
    1. 计算快速和慢速移动平均线
    2. 当快线上穿慢线时做多
    3. 当快线下穿慢线时做空
    4. 持有反向仓位时，先平仓再开新仓


    特点:
    - 经典趋势跟踪策略，适合有明显趋势的市场
    - 小窗口参数应对短期趋势，大窗口参数适合长期趋势
    - 简单且经过市场验证的策略逻辑


    策略核心执行流程:

    1. 小时K线数据更新 (on_hour_bar)
       |
    2. 计算快速与慢速移动平均线
       |
    3. 判断均线交叉情况
       |
       ├── 快线上穿慢线:
       |    ├── 无仓位: 做多
       |    ├── 空头仓位: 平空开多
       |
       ├── 快线下穿慢线:
       |    ├── 无仓位: 做空
       |    ├── 多头仓位: 平多开空
    """

    author: str = "VeighNa AI"

    # 策略参数
    fast_window: int = 10          # 快速移动平均线窗口，影响快速均线计算周期，建议5-15
    slow_window: int = 20          # 慢速移动平均线窗口，影响慢速均线计算周期，建议15-60

    # 策略变量
    fast_ma0: float = 0.0          # 当前快速移动平均线，最新K线的快速MA值，用于判断均线交叉
    fast_ma1: float = 0.0          # 上一期快速移动平均线，前一根K线的快速MA值，用于判断均线交叉

    slow_ma0: float = 0.0          # 当前慢速移动平均线，最新K线的慢速MA值，用于判断均线交叉
    slow_ma1: float = 0.0          # 上一期慢速移动平均线，前一根K线的慢速MA值，用于判断均线交叉

    # 参数名称列表
    parameters: list[str] = [
        "fast_window",
        "slow_window"
    ]

    # 变量名称列表
    variables: list[str] = [
        "fast_ma0",
        "fast_ma1",
        "slow_ma0",
        "slow_ma1"
    ]

    def on_init(self) -> None:
        """
        策略初始化回调函数

        作用：
            在策略启动时执行一次，用于初始化策略所需的变量和组件

        执行流程：
            1. 打印初始化日志
            2. 加载历史K线数据，准备计算初始技术指标
        """
        self.write_log("策略初始化")

        # 创建K线生成器：将Tick数据合成1小时K线
        self.bg = BarGenerator(
            self.on_bar,
            window=1,
            on_window_bar=self.on_hour_bar,
            interval=Interval.HOUR
        )

        # 创建K线时序数据管理器：计算技术指标
        self.am = ArrayManager()

        # 加载历史数据用于初始化回测
        self.load_bar(10)

    def on_start(self) -> None:
        """
        策略启动回调函数

        作用：
            在交易引擎启动策略时调用一次
            用于在策略正式运行前做最后的准备工作

        执行逻辑：
            1. 输出策略启动日志
            2. 推送策略状态更新事件
        """
        self.write_log("策略启动")

    def on_stop(self) -> None:
        """
        策略停止回调函数

        作用：
            在交易引擎停止策略时调用一次
            用于在策略停止运行时进行清理工作

        执行逻辑：
            1. 输出策略停止日志
            2. 推送策略状态更新事件
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """
        Tick数据更新回调函数

        作用：
            处理最新的市场Tick数据

        参数：
            tick (TickData)：最新的市场Tick数据对象

        执行逻辑：
            将Tick数据传入K线生成器，用于合成1小时K线
        """
        # 更新K线生成器
        self.bg.update_tick(tick)

    def on_bar(self, bar: BarData) -> None:
        """
        K线数据更新回调函数

        作用：
            处理常规K线数据（通常是1分钟K线）

        参数：
            bar (BarData)：最新的K线数据对象

        执行逻辑：
            将分钟K线传入K线生成器，用于合成1小时K线
        """
        # 更新1小时K线
        self.bg.update_bar(bar)

    def on_hour_bar(self, bar: BarData) -> None:
        """
        小时K线数据更新回调函数

        作用：
            处理合成的1小时K线数据，执行策略核心交易逻辑

        参数：
            bar (BarData)：最新的1小时K线数据对象

        执行流程：
            1. 撤销之前的所有挂单
            2. 更新K线数据到数组管理器并检查初始化状态
            3. 计算快速与慢速移动平均线
            4. 判断均线交叉信号
            5. 根据交叉信号和当前持仓执行交易操作
            6. 推送策略状态更新
        """
        # 撤销所有活动委托
        self.cancel_all()

        # 更新K线数据到时序数据管理器
        am = self.am
        am.update_bar(bar)

        # 检查是否已经初始化
        if not am.inited:
            return

        # 计算快速移动平均线
        fast_ma = am.sma(self.fast_window, array=True)
        self.fast_ma0 = fast_ma[-1]  # 当前快速均线
        self.fast_ma1 = fast_ma[-2]  # 上一期快速均线

        # 计算慢速移动平均线
        slow_ma = am.sma(self.slow_window, array=True)
        self.slow_ma0 = slow_ma[-1]  # 当前慢速均线
        self.slow_ma1 = slow_ma[-2]  # 上一期慢速均线

        # 判断均线交叉
        cross_over = self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1  # 金叉：快线上穿慢线
        cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1  # 死叉：快线下穿慢线

        # 根据交叉信号执行交易
        if cross_over:  # 金叉信号
            if self.pos == 0:  # 无持仓，直接做多
                self.buy(bar.close_price, 1)
            elif self.pos < 0:  # 持有空头，先平空再做多
                self.cover(bar.close_price, 1)
                self.buy(bar.close_price, 1)

        elif cross_below:  # 死叉信号
            if self.pos == 0:  # 无持仓，直接做空
                self.short(bar.close_price, 1)
            elif self.pos > 0:  # 持有多头，先平多再做空
                self.sell(bar.close_price, 1)
                self.short(bar.close_price, 1)

        # 更新图形界面
        self.put_event()

    def on_order(self, order: OrderData) -> None:
        """
        委托更新回调函数

        作用：
            处理委托单状态更新事件
            用于跟踪订单状态、分析成交情况等

        参数：
            order (OrderData)：委托订单数据对象

        执行逻辑：
            本策略不需要对委托状态变化做特殊处理
        """
        pass

    def on_trade(self, trade: TradeData) -> None:
        """
        成交更新回调函数

        作用：
            处理成交回报事件
            记录交易状态、更新持仓信息、发送通知等

        参数：
            trade (TradeData)：成交数据对象

        执行逻辑：
            本策略不使用停止单功能，无需特殊处理
        """
        pass

    def on_stop_order(self, stop_order: StopOrder) -> None:
        """
        停止单更新回调函数

        作用：
            处理本地停止单状态变化事件
            用于跟踪停止单触发、撤销等状态

        参数：
            stop_order (StopOrder)：停止单数据对象

        执行逻辑：
            本策略不使用停止单功能，无需特殊处理
        """
        pass

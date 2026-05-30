"""
VeighNa策略关键词:
Dual Thrust, 日内交易, 区间突破, 趋势跟踪, 开盘价区间, 价格突破,
尾盘平仓, 不隔夜持仓, 当日高低点, 价格区间, 上下轨系数,
动态通道, 价格波动, 不同系数, 开盘区间, 短线交易,
日内波动, 高波动市场, 反转策略, 日内趋势
"""

from datetime import time
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


class DualThrustStrategy(CtaTemplate):
    """
    基于Dual Thrust的日内趋势跟踪策略


    策略逻辑:
    1. 开盘价基础上计算上下轨突破通道
       - 上轨 = 开盘价 + K1 * 前一日价格区间
       - 下轨 = 开盘价 - K2 * 前一日价格区间
    2. 价格突破上轨，开多仓
    3. 价格突破下轨，开空仓
    4. 尾盘时间平仓锁定利润


    特点:
    - 趋势跟踪型，适合日内波动明显的市场
    - 基于开盘价建立上下轨通道
    - 设定尾盘时间强制平仓，不隔夜持仓


    策略核心执行流程:

    1. K线数据更新 (on_bar)
       |
    2. 判断是否为新交易日
       |
       ├── 是新交易日:
       |    └── 计算当日的上下轨道水平
       |
    3. 更新当日最高最低价
       |
    4. 交易时段内执行突破策略
       |
       ├── 无持仓:
       |    ├── 价格高于开盘价: 考虑开多
       |    └── 价格低于开盘价: 考虑开空
       |
    5. 收盘前强制平仓
    """

    author: str = "VeighNa AI"

    # 策略参数
    fixed_size: int = 1                     # 固定交易数量，每次交易的合约数
    k1: float = 0.4                         # 上轨系数，影响上轨通道宽度
    k2: float = 0.6                         # 下轨系数，影响下轨通道宽度

    # 策略变量
    day_open: float = 0                     # 当日开盘价格
    day_high: float = 0                     # 当日最高价格
    day_low: float = 0                      # 当日最低价格
    day_range: float = 0                    # 前一日的价格区间，用于计算当日通道
    long_entry: float = 0                   # 多头入场价格，上轨突破水平
    short_entry: float = 0                  # 空头入场价格，下轨突破水平
    long_entered: bool = False              # 是否已经开过多仓标志
    short_entered: bool = False             # 是否已经开过空仓标志

    # 参数名称列表
    parameters: list[str] = [
        "k1",
        "k2",
        "fixed_size"
    ]

    # 变量名称列表
    variables: list[str] = [
        "day_range",
        "long_entry",
        "short_entry",
        "long_entered",
        "short_entered"
    ]

    def on_init(self) -> None:
        """
        策略初始化回调

        作用:
            在策略启动时执行一次，用于初始化策略所需的变量和组件

        执行流程:
            1. 输出日志记录初始化信息
            2. 初始化K线缓存列表和尾盘平仓时间
            3. 创建K线生成器和数组管理器
            4. 加载历史K线数据
        """
        self.write_log("策略初始化")

        self.bars: list[BarData] = []                           # 缓存的K线数据列表
        self.exit_time: time = time(hour=14, minute=55)         # 平仓时间，当日交易结束前平仓

        self.bg: BarGenerator = BarGenerator(self.on_bar)
        self.am: ArrayManager = ArrayManager()

        self.load_bar(10)

    def on_start(self) -> None:
        """
        策略启动回调

        作用:
            在交易引擎启动策略时调用一次
            用于标记策略开始运行

        执行流程:
            输出日志记录策略启动信息
        """
        self.write_log("策略启动")

    def on_stop(self) -> None:
        """
        策略停止回调

        作用:
            在交易引擎停止策略时调用一次
            用于标记策略停止运行

        执行流程:
            输出日志记录策略停止信息
        """
        self.write_log("策略停止")

    def on_tick(self, tick: TickData) -> None:
        """
        新的Tick数据更新回调

        作用:
            处理最新的市场Tick数据
            用于实时更新市场状态和策略判断

        参数:
            tick (TickData): 最新的市场Tick数据对象

        执行流程:
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
            1. 撤销之前的所有挂单
            2. 更新K线缓存并确保有足够数据
            3. 判断是否为新交易日并相应更新参数
               - 计算当日通道上下轨
               - 更新当日价格指标
               - 重置入场标志
            4. 更新当日最高最低价
            5. 交易时段内执行突破策略
               - 无持仓: 根据价格位置考虑开多或开空
               - 持有多仓: 设置反向突破平仓
               - 持有空仓: 设置反向突破平仓
            6. 尾盘时段执行强制平仓操作
            7. 推送策略状态更新
        """
        # 撤销之前的所有委托
        self.cancel_all()

        # 添加新K线到缓存并确保有足够数据
        self.bars.append(bar)
        if len(self.bars) <= 2:
            return
        else:
            self.bars.pop(0)
        last_bar = self.bars[-2]

        # 检查是否为新交易日
        if last_bar.datetime.date() != bar.datetime.date():
            # 如果有昨日数据，计算今日通道
            if self.day_high:
                self.day_range = self.day_high - self.day_low
                self.long_entry = bar.open_price + self.k1 * self.day_range
                self.short_entry = bar.open_price - self.k2 * self.day_range

            # 更新今日开盘、最高、最低价
            self.day_open = bar.open_price
            self.day_high = bar.high_price
            self.day_low = bar.low_price

            # 重置入场标志
            self.long_entered = False
            self.short_entered = False
        else:
            # 更新当日最高最低价
            self.day_high = max(self.day_high, bar.high_price)
            self.day_low = min(self.day_low, bar.low_price)

        # 如果没有计算出通道宽度，退出
        if not self.day_range:
            return

        # 判断是否在交易时段内
        if bar.datetime.time() < self.exit_time:
            # 根据持仓情况执行不同策略
            if self.pos == 0:
                # 无持仓，根据价格位置决定突破方向
                if bar.close_price > self.day_open:
                    if not self.long_entered:
                        self.buy(self.long_entry, self.fixed_size, stop=True)
                else:
                    if not self.short_entered:
                        self.short(self.short_entry,
                                   self.fixed_size, stop=True)

            elif self.pos > 0:
                # 持有多仓，设置反向突破平仓并开反向仓
                self.long_entered = True

                self.sell(self.short_entry, self.fixed_size, stop=True)

                if not self.short_entered:
                    self.short(self.short_entry, self.fixed_size, stop=True)

            elif self.pos < 0:
                # 持有空仓，设置反向突破平仓并开反向仓
                self.short_entered = True

                self.cover(self.long_entry, self.fixed_size, stop=True)

                if not self.long_entered:
                    self.buy(self.long_entry, self.fixed_size, stop=True)

        else:
            # 尾盘时间强制平仓
            if self.pos > 0:
                self.sell(bar.close_price * 0.99, abs(self.pos))
            elif self.pos < 0:
                self.cover(bar.close_price * 1.01, abs(self.pos))

        # 推送策略状态更新
        self.put_event()

    def on_order(self, order: OrderData) -> None:
        """
        新的订单数据更新回调

        作用:
            处理委托单状态更新事件
            用于跟踪订单状态、分析成交情况等

        参数:
            order (OrderData): 委托订单数据对象

        执行逻辑:
            本策略中不需要特别处理订单更新
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
            本策略中不需要特别处理成交更新
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

        执行逻辑:
            本策略中不需要特别处理停止单更新
        """
        pass

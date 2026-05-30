# CtaTemplate 策略模板API参考

CtaTemplate是所有CTA策略的基类，定义了策略生命周期和交易接口。

## 类属性

```python
class MyStrategy(CtaTemplate):
    author = "作者名"
    parameters = ["fast_window", "slow_window", "fixed_size"]  # 可优化参数
    variables = ["fast_ma", "slow_ma"]                          # 实时显示变量
```

## 实例属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `self.pos` | float | 当前持仓量（正=多头，负=空头，0=空仓） |
| `self.inited` | bool | 策略是否已初始化 |
| `self.trading` | bool | 策略是否在交易中 |
| `self.vt_symbol` | str | 合约代码（如 rb2501.SHFE） |
| `self.strategy_name` | str | 策略实例名称 |

## 生命周期回调

```python
def on_init(self):
    """策略初始化时调用。必须实现。通常在此加载历史数据。"""
    self.load_bar(10)  # 加载10天历史K线用于指标预热

def on_start(self):
    """策略启动时调用"""

def on_stop(self):
    """策略停止时调用"""
```

## 数据回调

```python
def on_tick(self, tick: TickData):
    """收到新Tick数据时调用"""

def on_bar(self, bar: BarData):
    """收到新K线数据时调用（核心策略逻辑写在这里）"""

def on_order(self, order: OrderData):
    """委托状态更新时调用"""

def on_trade(self, trade: TradeData):
    """成交回报时调用"""

def on_stop_order(self, stop_order: StopOrder):
    """本地停止单状态更新时调用"""
```

## 交易方法

| 方法 | 方向 | 开平 | 说明 |
|------|------|------|------|
| `self.buy(price, volume)` | 多 | 开仓 | 买入开多 |
| `self.sell(price, volume)` | 空 | 平仓 | 卖出平多 |
| `self.short(price, volume)` | 空 | 开仓 | 卖出开空 |
| `self.cover(price, volume)` | 多 | 平仓 | 买入平空 |

### 参数说明

```python
self.buy(
    price: float,      # 委托价格
    volume: float,     # 委托数量
    stop: bool = False,  # True=本地停止单（触发后才发出）
    lock: bool = False,  # True=锁仓模式（上期所）
    net: bool = False    # True=净仓模式
) -> list[str]         # 返回委托ID列表
```

### 典型用法

```python
# 限价单开多
self.buy(bar.close_price + 5, 1)

# 停止单开多（突破入场）
self.buy(self.entry_price, 1, stop=True)

# 平仓
if self.pos > 0:
    self.sell(bar.close_price - 5, abs(self.pos))
elif self.pos < 0:
    self.cover(bar.close_price + 5, abs(self.pos))
```

## 委托管理

```python
self.cancel_order(vt_orderid)  # 撤销指定委托
self.cancel_all()              # 撤销所有活动委托
```

## 辅助方法

```python
self.write_log("日志消息")           # 输出日志
self.get_engine_type()              # 返回引擎类型（BACKTESTING/LIVE）
self.get_pricetick()                # 获取最小价格变动
self.get_size()                     # 获取合约乘数
self.put_event()                    # 触发UI更新
self.send_email("邮件内容")          # 发送邮件通知
self.sync_data()                    # 同步策略数据到磁盘
```

## 数据加载

```python
self.load_bar(
    days: int,                        # 加载天数
    interval: Interval = Interval.MINUTE,  # K线周期
    callback: Callable = self.on_bar,      # 数据回调函数
    use_database: bool = False             # True=强制从数据库加载
)

self.load_tick(days: int)  # 加载Tick数据
```

## TargetPosTemplate（目标仓位模板）

继承自CtaTemplate，提供基于目标仓位的交易逻辑：

```python
class MyStrategy(TargetPosTemplate):
    def on_bar(self, bar: BarData):
        # 只需设置目标仓位，模板自动处理开平仓
        if signal_long:
            self.set_target_pos(1)
        elif signal_short:
            self.set_target_pos(-1)
        else:
            self.set_target_pos(0)
```

TargetPosTemplate自动处理：
- 当前仓位与目标仓位的差值计算
- 多转空、空转多的中间平仓步骤
- 委托价格（基于最新tick或bar的价格 ± tick_add）
- 未成交委托的撤单和重发

## CtaSignal（信号组件）

用于将策略拆分为多个独立信号：

```python
class TrendSignal(CtaSignal):
    def on_bar(self, bar: BarData):
        # 计算信号
        if trend_up:
            self.set_signal_pos(1)
        elif trend_down:
            self.set_signal_pos(-1)

class MyStrategy(CtaTemplate):
    def __init__(self, ...):
        self.trend_signal = TrendSignal()
        self.mean_signal = MeanReversionSignal()

    def on_bar(self, bar: BarData):
        self.trend_signal.on_bar(bar)
        self.mean_signal.on_bar(bar)
        # 综合多个信号
        target_pos = self.trend_signal.get_signal_pos() + self.mean_signal.get_signal_pos()
```

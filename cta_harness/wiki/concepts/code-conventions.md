# 策略代码规范

从参考策略中提取的命名风格、helper函数写法和代码最佳实践。

## 参数命名风格

snake_case，带描述性后缀：

```python
# 指标周期：{indicator}_window
boll_window: int = 58
atr_window: int = 6
rsi_window: int = 7
aroon_window: int = 18

# 倍数/系数：{purpose}_multiplier 或 {purpose}_dev
boll_dev: float = 2.8
stop_multiplier: float = 2.1

# 百分比：trailing_percent / trailing_long
trailing_percent: float = 0.5
trailing_long: float = 0.5

# 风险/仓位
risk_level: int = 300
fixed_size: int = 1

# 通道系数
k1: float = 0.4
k2: float = 0.6

# 周期
window: int = 15
```

## 变量命名风格

snake_case，带描述性前缀：

```python
# 指标值：{indicator}_value 或 {indicator}_up/down
boll_up: float = 0.0
boll_down: float = 0.0
atr_value: float = 0.0
rsi_value: float = 0.0
cci_value: float = 0.0
aroon_up: float = 0.0
aroon_down: float = 0.0

# 价格水平：{direction}_{purpose}
long_entry: float = 0.0
short_entry: float = 0.0
long_stop: float = 0.0
short_stop: float = 0.0

# 持仓期间追踪
intra_trade_high: float = 0.0
intra_trade_low: float = 0.0

# 状态标记
long_entered: bool = False
short_entered: bool = False
daily_count: int = 0

# 计算得出的仓位
trade_size: int = 1
trading_size: int = 1
```

## Helper辅助函数写法

### 模式1：指标集中计算

```python
def calculate_indicators(self) -> None:
    """集中计算所有技术指标"""
    self.boll_up, self.boll_down = self.am.boll(self.boll_window, self.boll_dev)
    self.aroon_up, self.aroon_down = self.am.aroon(self.aroon_window)
    self.atr_value = self.am.atr(self.atr_window)
```

### 模式2：条件检查（返回bool）

```python
def check_trend_by_atr(self) -> bool:
    """波动率过滤：只在ATR高于均值时交易"""
    return self.atr_value > self.atr_ma
```

### 模式3：按持仓状态分发

```python
def handle_no_position(self, bar: BarData) -> None:
    """空仓时的入场逻辑"""
    self.trading_size = int(self.risk_level / self.atr_value)
    if self.aroon_up > self.aroon_down:
        self.buy(self.boll_up, self.trading_size, True)
    else:
        self.short(self.boll_down, self.trading_size, True)

def update_long_position(self, bar: BarData) -> None:
    """多头持仓管理"""
    self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
    self.long_stop = self.intra_trade_high - self.atr_value * self.stop_multiplier
    self.sell(self.long_stop, abs(self.pos), True)
```

### 模式4：金字塔下单

```python
def send_buy_orders(self, price: float) -> None:
    """分批挂多头停止单"""
    t = self.pos / self.fixed_size
    if t < 1:
        self.buy(price, self.fixed_size, True)
    if t < 2:
        self.buy(price + self.atr_value * 0.5, self.fixed_size, True)
```

### 模式5：日线重置

```python
def check_new_day(self, bar: BarData) -> None:
    """新交易日重置变量"""
    if self.last_bar.datetime.date() != bar.datetime.date():
        self.day_range = self.day_high - self.day_low
        self.long_entry = bar.open_price + self.k1 * self.day_range
        self.short_entry = bar.open_price - self.k2 * self.day_range
        self.day_open = bar.open_price
        self.day_high = bar.high_price
        self.day_low = bar.low_price
        self.daily_count = 0
```

## 代码风格Best Practice

### 类型提示

所有方法签名和类属性都使用类型提示：

```python
# 类属性
boll_window: int = 58
boll_up: float = 0.0
long_entered: bool = False

# 方法签名
def on_bar(self, bar: BarData) -> None: ...
def check_trend_by_atr(self) -> bool: ...
def send_buy_orders(self, price: float) -> None: ...
```

### Docstring

策略类使用中文多行docstring说明逻辑流程：

```python
def on_window_bar(self, bar: BarData) -> None:
    """
    窗口K线更新回调

    执行流程:
        1. 撤销之前的所有挂单
        2. 更新K线数据并检查初始化
        3. 计算技术指标
        4. 根据持仓状态执行对应逻辑
        5. 推送策略状态更新
    """
```

Helper函数用简短单行docstring：

```python
def check_trend_by_atr(self) -> bool:
    """波动率过滤：只在ATR高于均值时交易"""
```

### 行内注释

只在非显而易见的逻辑处添加：

```python
# 撤销之前的所有委托
self.cancel_all()

# 多头持仓时，更新最高价并计算止损价
self.intra_trade_high = max(self.intra_trade_high, bar.high_price)

# t = 当前持仓单位数
t = self.pos / self.fixed_size
```

### on_bar标准结构

```python
def on_window_bar(self, bar: BarData) -> None:
    # 1. 撤单
    self.cancel_all()

    # 2. 更新数据
    self.am.update_bar(bar)
    if not self.am.inited:
        return

    # 3. 计算指标
    self.calculate_indicators()

    # 4. 交易逻辑（按持仓状态分支）
    if self.pos == 0:
        self.handle_no_position(bar)
    elif self.pos > 0:
        self.update_long_position(bar)
    elif self.pos < 0:
        self.update_short_position(bar)

    # 5. 推送更新
    self.put_event()
```

### parameters/variables列表

显式声明，每行一个：

```python
parameters: list[str] = [
    "boll_window",
    "boll_dev",
    "aroon_window",
    "atr_window",
    "stop_multiplier",
    "risk_level",
    "window",
]

variables: list[str] = [
    "boll_up",
    "boll_down",
    "atr_value",
    "trade_size",
    "long_stop",
    "short_stop",
]
```

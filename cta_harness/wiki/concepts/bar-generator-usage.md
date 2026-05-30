# BarGenerator K线合成器

BarGenerator用于将低周期K线合成为高周期K线，或从Tick数据合成1分钟K线。

## 基本用法

### 仅使用1分钟K线

```python
def __init__(self, ...):
    self.bg = BarGenerator(self.on_bar)
    self.am = ArrayManager()

def on_tick(self, tick: TickData):
    self.bg.update_tick(tick)

def on_bar(self, bar: BarData):
    am = self.am
    am.update_bar(bar)
    if not am.inited:
        return
    # 策略逻辑...
```

### 合成N分钟K线

```python
def __init__(self, ...):
    self.bg = BarGenerator(self.on_bar, window=5, on_window_bar=self.on_5min_bar)
    self.am = ArrayManager()

def on_bar(self, bar: BarData):
    self.bg.update_bar(bar)

def on_5min_bar(self, bar: BarData):
    am = self.am
    am.update_bar(bar)
    if not am.inited:
        return
    # 策略逻辑在5分钟K线上执行...
```

### 合成小时K线

```python
def __init__(self, ...):
    self.bg = BarGenerator(
        self.on_bar,
        window=1,
        on_window_bar=self.on_hour_bar,
        interval=Interval.HOUR
    )

def on_bar(self, bar: BarData):
    self.bg.update_bar(bar)

def on_hour_bar(self, bar: BarData):
    # 策略逻辑在1小时K线上执行...
```

### 合成N小时K线

```python
self.bg = BarGenerator(
    self.on_bar,
    window=4,
    on_window_bar=self.on_4hour_bar,
    interval=Interval.HOUR
)
```

### 合成日K线

```python
from datetime import time

self.bg = BarGenerator(
    self.on_bar,
    window=1,
    on_window_bar=self.on_daily_bar,
    interval=Interval.DAILY,
    daily_end=time(15, 0)  # 必须指定收盘时间
)
```

## 构造函数参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `on_bar` | Callable | 1分钟K线回调（从tick合成时触发） |
| `window` | int | 合成窗口大小（默认0，不合成） |
| `on_window_bar` | Callable | 合成K线完成时的回调 |
| `interval` | Interval | 合成目标周期：MINUTE/HOUR/DAILY |
| `daily_end` | time | 日K线收盘时间（合成日线时必填） |

## 支持的合成周期

| 目标周期 | window值 | interval | 约束 |
|----------|----------|----------|------|
| N分钟 | N (2,3,5,6,10,15,20,30) | MINUTE | N必须能整除60 |
| N小时 | N (任意) | HOUR | 无限制 |
| 日线 | 1 | DAILY | 必须传daily_end |

## 多周期组合模式

```python
def __init__(self, ...):
    # 第一层：1分钟 → 15分钟
    self.bg15 = BarGenerator(self.on_bar, window=15, on_window_bar=self.on_15min_bar)
    self.am15 = ArrayManager()

    # 第二层：1分钟 → 1小时
    self.bg60 = BarGenerator(self.on_bar, window=1, on_window_bar=self.on_hour_bar, interval=Interval.HOUR)
    self.am60 = ArrayManager()

def on_bar(self, bar: BarData):
    self.bg15.update_bar(bar)
    self.bg60.update_bar(bar)

def on_15min_bar(self, bar: BarData):
    self.am15.update_bar(bar)
    # 短周期信号...

def on_hour_bar(self, bar: BarData):
    self.am60.update_bar(bar)
    # 长周期趋势判断...
```

## 注意事项

- `update_tick()` 用于从Tick合成1分钟K线
- `update_bar()` 用于从1分钟K线合成更高周期
- 分钟合成的判断条件是 `(minute + 1) % window == 0`
- 小时合成在分钟为59时或小时切换时触发
- `generate()` 方法可强制推送当前未完成的K线（用于收盘处理）

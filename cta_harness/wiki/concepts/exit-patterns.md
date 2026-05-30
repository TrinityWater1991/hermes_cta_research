# 平仓离场逻辑

## 1. 反向信号平仓

入场信号反转时平仓并反手。

```python
cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1

if cross_below and self.pos > 0:
    self.sell(bar.close_price, abs(self.pos))
    self.short(bar.close_price, self.fixed_size)
```

来源：double_ma_strategy.py

## 2. 反向通道突破

用较短周期的通道作为离场信号（入场用长周期，离场用短周期）。

```python
self.exit_up, self.exit_down = self.am.donchian(self.exit_window)

if self.pos > 0:
    sell_price = max(self.long_stop, self.exit_down)
    self.sell(sell_price, abs(self.pos), stop=True)
elif self.pos < 0:
    cover_price = min(self.short_stop, self.exit_up)
    self.cover(cover_price, abs(self.pos), stop=True)
```

来源：turtle_signal_strategy.py

## 3. 时间平仓（日内策略）

收盘前强制平仓，避免隔夜风险。

```python
from datetime import time

exit_time = time(hour=14, minute=55)

if bar.datetime.time() >= exit_time:
    if self.pos > 0:
        self.sell(bar.close_price * 0.99, abs(self.pos))
    elif self.pos < 0:
        self.cover(bar.close_price * 1.01, abs(self.pos))
```

来源：dual_thrust_strategy.py

## 4. 移动止损触发

见下方"移动止损逻辑"章节。

---

# 移动止损逻辑

## 1. ATR倍数止损

止损距离 = ATR × 倍数。随持仓期间最高/最低价移动。

```python
# 参数
stop_multiplier: float = 2.1

# 多头止损
self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
self.long_stop = self.intra_trade_high - self.atr_value * self.stop_multiplier
self.sell(self.long_stop, abs(self.pos), stop=True)

# 空头止损
self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
self.short_stop = self.intra_trade_low + self.atr_value * self.stop_multiplier
self.cover(self.short_stop, abs(self.pos), stop=True)
```

来源：pulse_strategy.py

## 2. 百分比移动止损

止损距离 = 最高价 × 百分比。

```python
# 参数
trailing_percent: float = 0.5

# 多头
self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
distance = self.intra_trade_high * self.trailing_percent / 100
self.long_stop = self.intra_trade_high - distance
self.sell(self.long_stop, abs(self.pos), stop=True)

# 空头
self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
distance = self.intra_trade_low * self.trailing_percent / 100
self.short_stop = self.intra_trade_low + distance
self.cover(self.short_stop, abs(self.pos), stop=True)
```

来源：atr_rsi_strategy.py

## 3. 布林带宽度止损

止损距离 = 布林带宽度 × 系数。波动大时止损宽，波动小时止损紧。

```python
# 参数
trailing_long: float = 0.5

boll_width = self.boll_up - self.boll_down
self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
self.long_stop = self.intra_trade_high - self.trailing_long * boll_width
self.sell(self.long_stop, abs(self.pos), stop=True)
```

来源：aegis_strategy.py

## 4. 固定ATR止损（不移动）

入场时设定止损价，持仓期间不调整。

```python
def on_trade(self, trade: TradeData) -> None:
    if trade.direction == Direction.LONG:
        self.long_stop = trade.price - 2 * self.atr_value
    else:
        self.short_stop = trade.price + 2 * self.atr_value
```

来源：turtle_signal_strategy.py

## 通用模式

所有移动止损都遵循相同结构：

```python
# 1. 开仓时重置追踪变量
if self.pos == 0:
    self.intra_trade_high = bar.high_price
    self.intra_trade_low = bar.low_price

# 2. 持仓时更新极值并计算止损
elif self.pos > 0:
    self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
    self.long_stop = self.intra_trade_high - stop_distance
    self.sell(self.long_stop, abs(self.pos), stop=True)

elif self.pos < 0:
    self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
    self.short_stop = self.intra_trade_low + stop_distance
    self.cover(self.short_stop, abs(self.pos), stop=True)
```

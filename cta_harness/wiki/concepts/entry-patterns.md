# 开仓入场逻辑

从参考策略中提取的常用入场信号模式。

## 1. 均线交叉

金叉做多，死叉做空。适合趋势跟踪。

```python
# 计算快慢均线（当前值和上一根值）
self.fast_ma0 = self.am.sma(self.fast_window)
self.slow_ma0 = self.am.sma(self.slow_window)

# 判断交叉
cross_over = self.fast_ma0 > self.slow_ma0 and self.fast_ma1 < self.slow_ma1
cross_below = self.fast_ma0 < self.slow_ma0 and self.fast_ma1 > self.slow_ma1

if cross_over:
    if self.pos == 0:
        self.buy(bar.close_price, self.fixed_size)
    elif self.pos < 0:
        self.cover(bar.close_price, abs(self.pos))
        self.buy(bar.close_price, self.fixed_size)
```

来源：double_ma_strategy.py

## 2. 通道突破（停止单）

价格突破通道上下轨时入场，使用stop=True挂停止单。

```python
# 唐奇安通道
self.entry_up, self.entry_down = self.am.donchian(self.entry_window)

if not self.pos:
    self.buy(self.entry_up, self.fixed_size, stop=True)
    self.short(self.entry_down, self.fixed_size, stop=True)
```

来源：turtle_signal_strategy.py

## 3. 布林带 + 方向过滤

用方向指标（CCI/Aroon）确定方向，在布林带边界挂停止单。

```python
self.boll_up, self.boll_down = self.am.boll(self.boll_window, self.boll_dev)
self.cci_value = self.am.cci(self.cci_window)

if not self.pos:
    if self.cci_value > 0:
        self.buy(self.boll_up, self.fixed_size, stop=True)
    elif self.cci_value < 0:
        self.short(self.boll_down, self.fixed_size, stop=True)
```

来源：boll_channel_strategy.py

## 4. 指标阈值

RSI/CCI等振荡指标超过阈值时入场。

```python
self.rsi_value = self.am.rsi(self.rsi_window)

if not self.pos:
    if self.rsi_value > 50 + self.rsi_signal:
        self.buy(bar.close_price + 5, self.fixed_size)
    elif self.rsi_value < 50 - self.rsi_signal:
        self.short(bar.close_price - 5, self.fixed_size)
```

来源：atr_rsi_strategy.py, surge_strategy.py

## 5. 日内突破（Dual Thrust）

基于前一日波幅计算当日突破价位。

```python
# 前日波幅
self.day_range = self.day_high - self.day_low
self.long_entry = bar.open_price + self.k1 * self.day_range
self.short_entry = bar.open_price - self.k2 * self.day_range

if not self.long_entered:
    self.buy(self.long_entry, self.fixed_size, stop=True)
if not self.short_entered:
    self.short(self.short_entry, self.fixed_size, stop=True)
```

来源：dual_thrust_strategy.py

---

# 趋势过滤方法

在入场前过滤弱趋势环境，提高信号质量。

## 1. ATR波动率过滤

只在波动率高于均值时交易（市场活跃时趋势更可靠）。

```python
self.atr_value = self.am.atr(self.atr_window)
self.atr_ma = self.am.sma(self.atr_window)  # ATR的均线

def check_trend_by_atr(self) -> bool:
    return self.atr_value > self.atr_ma

if not self.pos and self.check_trend_by_atr():
    # 执行入场逻辑...
```

来源：atr_rsi_strategy.py

## 2. Aroon方向

Aroon Up > Aroon Down表示上升趋势，反之下降趋势。

```python
self.aroon_up, self.aroon_down = self.am.aroon(self.aroon_window)

if self.aroon_up > self.aroon_down:
    self.buy(self.boll_up, self.trade_size, stop=True)
else:
    self.short(self.boll_down, self.trade_size, stop=True)
```

来源：pulse_strategy.py, aegis_strategy.py

## 3. CCI极性

CCI > 0为多头环境，CCI < 0为空头环境。

```python
self.cci_value = self.am.cci(self.cci_window)

if self.cci_value > 0:
    # 只做多
elif self.cci_value < 0:
    # 只做空
```

来源：boll_channel_strategy.py

## 4. RSI偏移阈值

RSI偏离50越远，趋势越强。

```python
# RSI > 50 + signal = 强上升趋势
# RSI < 50 - signal = 强下降趋势
if self.rsi_value >= 50 + self.rsi_signal:
    # 做多
elif self.rsi_value <= 50 - self.rsi_signal:
    # 做空
```

来源：surge_strategy.py

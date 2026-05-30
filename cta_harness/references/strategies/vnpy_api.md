# vnpy CTA 策略 API 速查表

## ArrayManager 功能说明

ArrayManager用于缓存收到的K线数据序列。

同一个ArrayManager对象，只能用于缓存一个时间级别的K线数据（bar对象）。即如果在on_15min_bar回调函数下要调用am.update_bar来缓存15分钟级别的K线，那么就不能同时在on_bar回调函数下也调用am.update_bar（会导致错误的将1分钟K线和后续的15分钟K线混合存储，造成实质上的逻辑错误）。

通常来说，对于不是1分钟级别的CTA策略，其on_bar回调函数下仅需要调用self.bg.update_bar来将1分钟K线合称为其他更长周期的K线，而不需要做其他多余处理，策略的核心逻辑应该移动到相关的on_window_bar回调函数下（如on_15min_bar）。

### 移动平均类

| 方法 | 说明 | 返回值 | 示例 |
|------|------|--------|------|
| `sma(n, array=False)` | 简单移动平均 | float / ndarray | `am.sma(20)` |
| `ema(n, array=False)` | 指数移动平均 | float / ndarray | `am.ema(20)` |
| `kama(n, array=False)` | 考夫曼自适应移动平均 | float / ndarray | `am.kama(30)` |
| `wma(n, array=False)` | 加权移动平均 | float / ndarray | `am.wma(20)` |

### 动量类

| 方法 | 说明 | 返回值 | 示例 |
|------|------|--------|------|
| `macd(fast, slow, signal, array=False)` | MACD | (macd, signal, hist) | `am.macd(12, 26, 9)` |
| `rsi(n, array=False)` | 相对强弱指数 | float (0-100) | `am.rsi(14)` |
| `mom(n, array=False)` | 动量 | float / ndarray | `am.mom(10)` |
| `roc(n, array=False)` | 变化率 | float / ndarray | `am.roc(10)` |
| `rocp(n, array=False)` | 变化率百分比 | float / ndarray | `am.rocp(10)` |
| `rocr(n, array=False)` | 变化率比率 | float / ndarray | `am.rocr(10)` |
| `rocr_100(n, array=False)` | 变化率比率(100基准) | float / ndarray | `am.rocr_100(10)` |
| `cmo(n, array=False)` | Chande动量振荡器 | float / ndarray | `am.cmo(14)` |
| `apo(fast, slow, matype=0, array=False)` | 绝对价格振荡器 | float / ndarray | `am.apo(12, 26)` |
| `ppo(fast, slow, matype=0, array=False)` | 百分比价格振荡器 | float / ndarray | `am.ppo(12, 26)` |
| `trix(n, array=False)` | 三重指数平滑平均 | float / ndarray | `am.trix(30)` |
| `willr(n, array=False)` | 威廉指标 | float / ndarray | `am.willr(14)` |
| `ultosc(p1=7, p2=14, p3=28, array=False)` | 终极振荡器 | float / ndarray | `am.ultosc(7, 14, 28)` |

### 趋势类

| 方法 | 说明 | 返回值 | 示例 |
|------|------|--------|------|
| `adx(n, array=False)` | 平均趋向指数 | float / ndarray | `am.adx(14)` |
| `adxr(n, array=False)` | 平均趋向指数评级 | float / ndarray | `am.adxr(14)` |
| `dx(n, array=False)` | 趋向指数 | float / ndarray | `am.dx(14)` |
| `plus_di(n, array=False)` | 正趋向指标 (+DI) | float / ndarray | `am.plus_di(14)` |
| `minus_di(n, array=False)` | 负趋向指标 (-DI) | float / ndarray | `am.minus_di(14)` |
| `plus_dm(n, array=False)` | 正趋向运动 (+DM) | float / ndarray | `am.plus_dm(14)` |
| `minus_dm(n, array=False)` | 负趋向运动 (-DM) | float / ndarray | `am.minus_dm(14)` |
| `aroon(n, array=False)` | Aroon指标 | (up, down) | `am.aroon(25)` |
| `aroonosc(n, array=False)` | Aroon振荡器 | float / ndarray | `am.aroonosc(25)` |
| `sar(accel, maximum, array=False)` | 抛物线SAR | float / ndarray | `am.sar(0.02, 0.2)` |

### 波动率类

| 方法 | 说明 | 返回值 | 示例 |
|------|------|--------|------|
| `atr(n, array=False)` | 平均真实波幅 | float / ndarray | `am.atr(14)` |
| `natr(n, array=False)` | 归一化平均真实波幅 | float / ndarray | `am.natr(14)` |
| `trange(array=False)` | 真实波幅 | float / ndarray | `am.trange()` |
| `std(n, nbdev=1, array=False)` | 标准差 | float / ndarray | `am.std(20)` |

### 通道类

| 方法 | 说明 | 返回值 | 示例 |
|------|------|--------|------|
| `boll(n, dev, array=False)` | 布林带 | (upper, lower) | `am.boll(20, 2)` |
| `keltner(n, dev, array=False)` | 肯特纳通道 | (upper, lower) | `am.keltner(20, 2)` |
| `donchian(n, array=False)` | 唐奇安通道 | (upper, lower) | `am.donchian(20)` |

### 成交量类

| 方法 | 说明 | 返回值 | 示例 |
|------|------|--------|------|
| `obv(array=False)` | 能量潮 (OBV) | float / ndarray | `am.obv()` |
| `mfi(n, array=False)` | 资金流量指数 | float / ndarray | `am.mfi(14)` |
| `ad(array=False)` | 累积/派发线 | float / ndarray | `am.ad()` |
| `adosc(fast, slow, array=False)` | 累积/派发振荡器 | float / ndarray | `am.adosc(3, 10)` |

### 其他指标

| 方法 | 说明 | 返回值 | 示例 |
|------|------|--------|------|
| `cci(n, array=False)` | 商品通道指数 | float / ndarray | `am.cci(14)` |
| `bop(array=False)` | 力量平衡 | float / ndarray | `am.bop()` |
| `stoch(fastk, slowk, slowk_ma, slowd, slowd_ma, array=False)` | 随机指标 KD | (k, d) | `am.stoch(5, 3, 0, 3, 0)` |

### 数据访问属性

| 属性 | 说明 | 类型 |
|------|------|------|
| `am.open` | 开盘价序列 | ndarray |
| `am.high` | 最高价序列 | ndarray |
| `am.low` | 最低价序列 | ndarray |
| `am.close` | 收盘价序列 | ndarray |
| `am.volume` | 成交量序列 | ndarray |
| `am.turnover` | 成交额序列 | ndarray |
| `am.open_interest` | 持仓量序列 | ndarray |

```python
am.close[-1]   # 最新收盘价
am.close[-2]   # 前一根 K 线收盘价
am.high[-10:]  # 最近 10 根 K 线最高价
am.inited      # 是否已初始化 (数据量 >= size)
```

---

## CtaTemplate 交易方法

| 方法 | 说明 | 示例 |
|------|------|------|
| `buy(price, volume)` | 买入开仓（做多） | `self.buy(bar.close_price, 1)` |
| `sell(price, volume)` | 卖出平仓（平多） | `self.sell(bar.close_price, 1)` |
| `short(price, volume)` | 卖出开仓（做空） | `self.short(bar.close_price, 1)` |
| `cover(price, volume)` | 买入平仓（平空） | `self.cover(bar.close_price, 1)` |

**持仓访问**:
```python
self.pos      # > 0 多头, < 0 空头, = 0 无持仓
```

---

## 常用品种配置

| 品种 | vt_symbol | size | pricetick |
|------|-----------|------|-----------|
| 螺纹钢 | rb99.SHFE | 10 | 1 |
| 铁矿石 | i99.DCE | 100 | 0.5 |
| 焦炭 | j99.DCE | 100 | 0.5 |
| 原油 | sc99.INE | 1000 | 0.1 |
| 沪铜 | cu99.SHFE | 5 | 10 |

---

## 常用策略模式

### 一、入场信号模式

#### 1. 均线交叉
快慢均线交叉是最经典的趋势跟踪信号，适用于趋势明显的市场。

```python
# 计算快慢均线（可选 sma/ema/kama）
fast_ma = am.sma(self.fast_window, array=True)
slow_ma = am.sma(self.slow_window, array=True)

# 判断金叉/死叉（需要前后两根K线对比）
cross_over = fast_ma[-1] > slow_ma[-1] and fast_ma[-2] < slow_ma[-2]
cross_below = fast_ma[-1] < slow_ma[-1] and fast_ma[-2] > slow_ma[-2]

if cross_over:
    if self.pos < 0:
        self.cover(bar.close_price, abs(self.pos))
    self.buy(bar.close_price, self.fixed_size)
elif cross_below:
    if self.pos > 0:
        self.sell(bar.close_price, abs(self.pos))
    self.short(bar.close_price, self.fixed_size)
```

#### 2. 通道突破 + 趋势过滤
使用通道（布林带/唐奇安/肯特纳）配合趋势指标（Aroon/CCI/RSI）过滤方向。

```python
# 计算通道和趋势指标
upper, lower = am.boll(self.boll_window, self.boll_dev)  # 或 donchian/keltner
trend_up, trend_down = am.aroon(self.aroon_window)       # 或用 cci/rsi 判断

# 趋势方向过滤 + 通道突破开仓（使用停止单）
if self.pos == 0:
    if trend_up > trend_down:       # 趋势向上
        self.buy(upper, self.fixed_size, stop=True)
    else:                           # 趋势向下
        self.short(lower, self.fixed_size, stop=True)
```

#### 3. 日内区间突破
基于开盘价和前日波动区间计算当日突破通道，适合日内交易。

```python
# 跨日时计算新通道（需在 on_bar 中检测日期变化）
if last_bar.datetime.date() != bar.datetime.date():
    if self.day_high:
        self.day_range = self.day_high - self.day_low
        self.long_entry = bar.open_price + self.k1 * self.day_range
        self.short_entry = bar.open_price - self.k2 * self.day_range
    # 重置日内变量
    self.day_open = bar.open_price
    self.day_high = bar.high_price
    self.day_low = bar.low_price
else:
    self.day_high = max(self.day_high, bar.high_price)
    self.day_low = min(self.day_low, bar.low_price)

# 突破开仓
if self.pos == 0:
    self.buy(self.long_entry, self.fixed_size, stop=True)
    self.short(self.short_entry, self.fixed_size, stop=True)
```

---

### 二、止损/出场模式

#### 1. ATR 倍数移动止损
根据市场波动率动态调整止损距离，是最常用的移动止损方式。

```python
atr = am.atr(self.atr_window)

if self.pos > 0:
    # 持续跟踪最高价
    self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
    # 止损价 = 最高价 - ATR × 倍数
    self.long_stop = self.intra_trade_high - atr * self.sl_multiplier
    self.sell(self.long_stop, abs(self.pos), stop=True)

elif self.pos < 0:
    self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
    self.short_stop = self.intra_trade_low + atr * self.sl_multiplier
    self.cover(self.short_stop, abs(self.pos), stop=True)
```

#### 2. 通道宽度移动止损
使用布林带或其他通道的宽度作为止损距离参考。

```python
upper, lower = am.boll(self.boll_window, self.boll_dev)
channel_width = upper - lower

if self.pos > 0:
    self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
    self.long_stop = self.intra_trade_high - self.trailing_pct * channel_width
    self.sell(self.long_stop, abs(self.pos), stop=True)

elif self.pos < 0:
    self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
    self.short_stop = self.intra_trade_low + self.trailing_pct * channel_width
    self.cover(self.short_stop, abs(self.pos), stop=True)
```

#### 3. 百分比移动止损
按价格百分比设置止损，简单直观。

```python
if self.pos > 0:
    self.intra_trade_high = max(self.intra_trade_high, bar.high_price)
    # 从最高价回撤 trailing_percent% 触发止损
    self.long_stop = self.intra_trade_high * (1 - self.trailing_percent / 100)
    self.sell(self.long_stop, abs(self.pos), stop=True)

elif self.pos < 0:
    self.intra_trade_low = min(self.intra_trade_low, bar.low_price)
    self.short_stop = self.intra_trade_low * (1 + self.trailing_percent / 100)
    self.cover(self.short_stop, abs(self.pos), stop=True)
```

#### 4. 通道反向突破出场
使用较短周期通道的反向突破作为离场信号（海龟法则）。

```python
# 入场通道（较长周期）和出场通道（较短周期）
entry_up, entry_down = am.donchian(self.entry_window)
exit_up, exit_down = am.donchian(self.exit_window)

if self.pos > 0:
    # 多头出场：取止损价和出场通道下轨的较大值
    sell_price = max(self.long_stop, exit_down)
    self.sell(sell_price, abs(self.pos), stop=True)

elif self.pos < 0:
    cover_price = min(self.short_stop, exit_up)
    self.cover(cover_price, abs(self.pos), stop=True)
```

#### 5. 尾盘强制平仓
日内策略在收盘前平仓，避免隔夜风险。

```python
from datetime import time
self.exit_time = time(hour=14, minute=55)

if bar.datetime.time() >= self.exit_time:
    if self.pos > 0:
        self.sell(bar.close_price * 0.99, abs(self.pos))  # 略低价确保成交
    elif self.pos < 0:
        self.cover(bar.close_price * 1.01, abs(self.pos))
```

---

### 三、仓位管理模式

#### 1. ATR 风险动态仓位
根据 ATR（波动率）动态计算开仓数量，控制单笔交易风险。

```python
atr = am.atr(self.atr_window)

# risk_level 代表愿意承受的风险金额
# 波动率越大，仓位越小；波动率越小，仓位越大
self.trading_size = max(1, int(self.risk_level / atr))

if self.pos == 0:
    self.buy(price, self.trading_size, stop=True)
```

#### 2. 金字塔分批加仓
按 ATR 间隔分批建仓，降低持仓成本（海龟交易法）。

```python
atr = am.atr(self.atr_window)
unit = self.pos / self.fixed_size  # 当前持仓单位数

# 多头金字塔加仓（最多4个单位）
if unit < 1:
    self.buy(price, self.fixed_size, stop=True)
if unit < 2:
    self.buy(price + atr * 0.5, self.fixed_size, stop=True)
if unit < 3:
    self.buy(price + atr * 1.0, self.fixed_size, stop=True)
if unit < 4:
    self.buy(price + atr * 1.5, self.fixed_size, stop=True)

# 空头金字塔加仓
if unit > -1:
    self.short(price, self.fixed_size, stop=True)
if unit > -2:
    self.short(price - atr * 0.5, self.fixed_size, stop=True)
# ... 以此类推
```

---

### 四、波动率过滤

在低波动率环境下避免开仓，只在波动率放大时交易。

```python
atr_array = am.atr(self.atr_window, array=True)
atr_current = atr_array[-1]
atr_ma = atr_array[-self.atr_ma_window:].mean()

# 只有当前 ATR 高于均值时才允许开仓
if atr_current > atr_ma:
    # 执行开仓逻辑
    if rsi > self.rsi_long_threshold:
        self.buy(bar.close_price, self.fixed_size)
    elif rsi < self.rsi_short_threshold:
        self.short(bar.close_price, self.fixed_size)
```

---

### 五、策略框架模板

#### 标准策略结构
```python
def on_init(self) -> None:
    self.bg = BarGenerator(self.on_bar, self.window, self.on_window_bar)
    self.am = ArrayManager()
    self.load_bar(10)

def on_bar(self, bar: BarData) -> None:
    self.bg.update_bar(bar)

def on_window_bar(self, bar: BarData) -> None:
    self.cancel_all()                    # 1. 撤销未成交委托
    self.am.update_bar(bar)
    if not self.am.inited:
        return
    
    self.calculate_indicators()          # 2. 计算技术指标
    
    if self.pos == 0:
        self.check_entry_signals(bar)    # 3. 检查开仓信号
    else:
        self.update_trailing_stop(bar)   # 4. 更新移动止损
    
    self.put_event()                     # 5. 推送状态更新
```

---

## 绩效指标参考

| 指标 | 说明 | 理想范围 |
|------|------|----------|
| sharpe_ratio | 夏普比率 | > 1.0 |
| max_ddpercent | 最大回撤 % | < 20% |
| winning_rate | 胜率 | > 40% |
| profit_factor | 盈亏比 | > 1.5 |
| total_trade_count | 交易次数 | 50-300/年 |

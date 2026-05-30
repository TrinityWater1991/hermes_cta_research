# ArrayManager 技术指标API参考

ArrayManager是VeighNa中用于管理K线时间序列和计算技术指标的核心工具类。底层基于TA-Lib实现。

## 初始化

```python
from vnpy.trader.utility import ArrayManager

am = ArrayManager(size=100)  # size: 缓存K线数量，默认100
```

## 数据更新

```python
am.update_bar(bar)  # 更新新K线数据
am.inited           # bool: 是否已积累足够数据（count >= size）
```

## 价格序列属性

| 属性 | 返回类型 | 说明 |
|------|----------|------|
| `am.open` | np.ndarray | 开盘价序列 |
| `am.high` | np.ndarray | 最高价序列 |
| `am.low` | np.ndarray | 最低价序列 |
| `am.close` | np.ndarray | 收盘价序列 |
| `am.volume` | np.ndarray | 成交量序列 |
| `am.turnover` | np.ndarray | 成交额序列 |
| `am.open_interest` | np.ndarray | 持仓量序列 |

## 通用规则

所有指标方法都支持 `array` 参数：
- `array=False`（默认）：返回最新一个值（float）
- `array=True`：返回完整序列（np.ndarray）

## 均线类

| 方法 | 参数 | 说明 |
|------|------|------|
| `am.sma(n)` | n: 周期 | 简单移动平均 |
| `am.ema(n)` | n: 周期 | 指数移动平均 |
| `am.kama(n)` | n: 周期 | 考夫曼自适应均线 |
| `am.wma(n)` | n: 周期 | 加权移动平均 |

## 动量类

| 方法 | 参数 | 说明 |
|------|------|------|
| `am.rsi(n)` | n: 周期 | 相对强弱指标 (0-100) |
| `am.cci(n)` | n: 周期 | 商品通道指标 |
| `am.mom(n)` | n: 周期 | 动量 |
| `am.roc(n)` | n: 周期 | 变动率 |
| `am.rocr(n)` | n: 周期 | 变动率比率 |
| `am.rocp(n)` | n: 周期 | 变动率百分比 |
| `am.rocr_100(n)` | n: 周期 | 变动率比率×100 |
| `am.cmo(n)` | n: 周期 | 钱德动量振荡器 |
| `am.trix(n)` | n: 周期 | 三重指数平滑均线变化率 |
| `am.willr(n)` | n: 周期 | 威廉指标 |
| `am.mfi(n)` | n: 周期 | 资金流量指标（含成交量） |
| `am.bop()` | 无 | 均势指标 |

## 趋势类

| 方法 | 参数 | 说明 |
|------|------|------|
| `am.adx(n)` | n: 周期 | 平均趋向指标 |
| `am.adxr(n)` | n: 周期 | ADX评估指标 |
| `am.dx(n)` | n: 周期 | 趋向指标 |
| `am.plus_di(n)` | n: 周期 | +DI方向指标 |
| `am.minus_di(n)` | n: 周期 | -DI方向指标 |
| `am.plus_dm(n)` | n: 周期 | +DM方向运动 |
| `am.minus_dm(n)` | n: 周期 | -DM方向运动 |
| `am.sar(acceleration, maximum)` | 加速因子, 最大值 | 抛物线SAR |
| `am.aroon(n)` | n: 周期 | Aroon指标，返回 (up, down) |
| `am.aroonosc(n)` | n: 周期 | Aroon振荡器 |

## 波动率类

| 方法 | 参数 | 说明 |
|------|------|------|
| `am.atr(n)` | n: 周期 | 平均真实波幅 |
| `am.natr(n)` | n: 周期 | 归一化ATR（百分比） |
| `am.trange()` | 无 | 真实波幅 |
| `am.std(n, nbdev=1)` | n: 周期, nbdev: 标准差倍数 | 标准差 |

## 通道类（返回元组）

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `am.boll(n, dev)` | n: 周期, dev: 标准差倍数 | (upper, lower) | 布林带 |
| `am.keltner(n, dev)` | n: 周期, dev: ATR倍数 | (upper, lower) | 肯特纳通道 |
| `am.donchian(n)` | n: 周期 | (upper, lower) | 唐奇安通道 |

## 复合指标

| 方法 | 参数 | 返回 | 说明 |
|------|------|------|------|
| `am.macd(fast, slow, signal)` | 快周期, 慢周期, 信号周期 | (macd, signal, hist) | MACD |
| `am.stoch(fastk, slowk, slowk_ma, slowd, slowd_ma)` | 5个参数 | (k, d) | 随机指标KD |
| `am.apo(fast, slow, matype=0)` | 快周期, 慢周期, MA类型 | float | 绝对价格振荡器 |
| `am.ppo(fast, slow, matype=0)` | 快周期, 慢周期, MA类型 | float | 百分比价格振荡器 |
| `am.ultosc(p1=7, p2=14, p3=28)` | 三个周期 | float | 终极振荡器 |

## 成交量类

| 方法 | 参数 | 说明 |
|------|------|------|
| `am.obv()` | 无 | 能量潮 |
| `am.ad()` | 无 | 累积/派发线 |
| `am.adosc(fast, slow)` | 快周期, 慢周期 | AD振荡器 |

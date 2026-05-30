# Correlation-Adjusted Time Series Momentum (TSMOM-CF) in Commodities Futures

**来源**: [QuantConnect Research](https://www.quantconnect.com/research/15272/improved-momentum-strategy-on-commodities-futures)  
**作者**: Alethea Lin  
**基于论文**: "Demystifying Time-Series Momentum Strategies: Volatility Estimators, Trading Rules and Pairwise Correlations" by Nick Baltas & Robert Kosowski  

---

## 核心思路

传统TSMOM使用过去N个月的收益作为信号（正=做多，负=做空），而本文提出了三个改进方向，均可单独用于单标的CTA策略。

### 方向1：统计显著性信号（TREND Rule）

用 **t-statistic** 替代简单的收益正负判断。

$$
\text{TREND}_i = \begin{cases}
+1, & \text{if } t(r) > +1 \\
t(r), & \text{if } -1 \leq t(r) \leq +1 \\
-1, & \text{if } t(r) < -1 \\
\end{cases}
$$

**含义**: 趋势的统计显著性越强，仓位越大。t-stat在[-1,1]之间时线性缩放。

### 方向2：Yang-Zhang波动率估计器

比收盘价标准差更高效的波动率估计，综合利用OHLC四个价格：
- 隔夜跳空波动（close-to-open）
- 日内波动范围（Rogers-Satchell区间估计器）
- 收盘价波动（close-to-close）

### 方向3：波动率目标仓位管理

$$
\text{Position} = \text{Signal} \times \frac{\sigma_{target}}{\sigma_{realized}}
$$

目标波动率12%，根据实际波动率动态调整仓位大小。

---

## 单标的CTA适配思路

原论文和实现针对多资产组合（含相关性调整因子CF），以下三个方向均可单独适配为单品种CTA：

| 方向 | 信号 | 适用品种 | 优势 |
|------|------|----------|------|
| v1: t-stat趋势信号 | 月频调仓，1日K线，信号=clip(t-stat,-1,1) | 所有 | 连续仓位，统计显著可解释 |
| v2: 波动率目标仓位 | v1 + 动态仓位 = signal × σ_tgt/σ_YZ | 高波动品种 | 风险平价，低波动时加仓 |
| v3: 多周期t-stat综合 | 多个lookback的t-stat加权平均 | 趋势性品种 | 多时间尺度确认 |

---

## 本文API参考

### TREND信号计算
```python
log_returns = np.log(close/close.shift(1)).dropna()
mean = np.mean(log_returns)
std = np.std(log_returns)
n = len(log_returns)
t_stat = mean/(std/np.sqrt(n))
signal = np.clip(t_stat, a_max=1, a_min=-1)
```

### Yang-Zhang波动率
```python
k = 0.34 / (1.34 + (N + 1) / (N - 1))
sigma_YZ^2 = sigma_OJ^2 + k * sigma_SD^2 + (1-k) * sigma_RS^2
```

---

**相关概念**: `wiki/concepts/` — 波动率估计、t-stat信号、波动率目标
**特有概念**: Yang-Zhang波动率、t-stat仓位缩放

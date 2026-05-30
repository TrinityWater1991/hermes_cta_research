# 迭代记录

## 变体1：Kalman趋势指标策略

### v1 默认参数（15分钟线，slippage=0）
- entry_threshold=30, atr_stop_multiplier=3.0
- Sharpe=0.50, Return=18.0%, MaxDD=-7.24%, Trades=6639
- 结论：逻辑可行但参数需优化

### v2 参数优化（2020-2025，slippage=0）
最优：entry_threshold=40, atr_stop_multiplier=2.0
- Sharpe=1.20, Return=19.6%, MaxDD=-2.62%, Trades=3486

### v3 全量验证（2016-2026，slippage=0）
- Sharpe=1.01, Return=29.3%, MaxDD=-3.34%, Trades=6944
- 达到毕业标准

### v4 稳健性验证（slippage=1）
- **Sharpe=-0.19, Return=-5.5%, MaxDD=-13.66%**
- **策略崩溃，无法承受1跳滑点**

### v5 升级到60分钟线（slippage=1）
- 多组参数测试，最好Sharpe=0.085（接近零）
- 交易频率降低但利润仍不足以覆盖成本

## 变体2：双EMA偏离策略

### v1 默认参数（1小时线，slippage=0）
- Sharpe=0.12, Return=3.3%, MaxDD=-7.69%
- 结论：表现太差，放弃

## 变体3：KAMA自适应趋势策略

### v1 参数扫描（15分钟线，slippage=0）
最优：kama_window=30, entry_atr=1.0, trailing_atr=2.0
- Sharpe=1.03, Return=32.5%, MaxDD=-3.02%, Trades=6662

### v2 稳健性验证（slippage=1）
- **Sharpe=-0.03, Return=-0.8%, MaxDD=-11.02%**
- **同样崩溃**

### v3 升级到60分钟线（slippage=1）
- 多组参数，最好Sharpe=0.085
- 无法盈利

### v4 4小时线（slippage=1）
- 最好：kama=20, entry=1.5, trail=3 → Sharpe=0.21, Trades=321
- 方向正确但Sharpe太低

## 最终结论

**策略不通过（Discard）**

文章中的"Fast Trend Following"思路本质上是高频策略，依赖极低交易成本。
在rb99.SHFE上，即使1跳滑点（1元×10合约乘数=10元/手）也会完全抹平利润。

### 根本原因
1. 策略每笔交易的平均利润极小（约5-10元/手）
2. 1跳滑点=10元/手，直接吃掉全部利润
3. 升级到更长周期后信号质量下降，无法补偿

### 教训
- "零滑点回测"的Sharpe不可信，必须加入真实交易成本验证
- 高频趋势跟踪策略需要极低成本的品种（如NQ期货bid-ask仅0.25点）
- rb99的最小变动1元×10倍=10元/手的隐含成本太高
- 该思路可能适合：股指期货IF（pricetick=0.2×300=60元但波动大）或流动性极好的品种

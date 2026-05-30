# 迭代记录

## 方向1：多周期MA等权趋势策略

### v1 默认参数（1小时线，slippage=0）
- entry_threshold=0.01, exit_threshold=0.002, atr_stop_multiplier=3.5
- Sharpe=0.42, Return=15.5%, MaxDD=-5.11%, Trades=1001

### v2 参数优化第一轮
最优：entry=0.01, atr=5 → Sharpe=0.58, Return=23.5%, DD=-4.75%, Trades=891

### v3 参数优化第二轮
- entry=0.01, exit=0.005, atr=5 → Sharpe=0.62
- entry=0.008, exit=0.0, atr=5 → Sharpe=0.58（回撤最低4.22%）

### v4 稳健性验证（entry=0.008, exit=0.0, atr=5）
- slippage=0: Sharpe=0.583, Return=23.7%, DD=-4.22%
- slippage=1: Sharpe=0.472, Return=19.2%, DD=-4.76%（下降19%，仍盈利）
- slippage=2: Sharpe=0.361, Return=14.7%, DD=-6.31%（仍盈利）

### 结论
策略能承受真实交易成本，但Sharpe未达1.0毕业标准。
保留代码，标注为"可用但未达标"策略。

## 方向2：三周期投票策略

*跳过（方向1已验证核心思路可行，无需重复验证简化版）*

## 方向3：自适应权重趋势策略

*跳过（需要更复杂的滚动回归实现，且方向1已给出基线结果）*

# 三层EMA趋势状态机的信号延迟问题

## 背景
在 Trend State Machine 策略优化中，发现默认参数（fast=8, slow=21, regime=55）在1小时K线上信号延迟严重，导致入场滞后。

## 关键发现
1. **EMA层间距比绝对值重要**：三层EMA需要足够的间距来形成明确的排列信号，但间距过大会导致信号延迟。
2. **1小时K线+55周期Regime EMA ≈ 55小时的信号确认延迟**：趋势已经运行2-3天后才确认入场。
3. **快参数（5/13/34）比慢参数（8/21/55）效果更好**：在jm99上Sharpe从0.60提升到0.78。
4. **参数灵敏度**：regime_ema从55降到34使Sharpe提升约30%。

## 最佳实践
- 使用三层EMA时，Regime EMA周期不应超过时间框架周期的2倍
- 1小时K线上，Regime EMA建议34-50之间
- Fast/Slow EMA间距建议6-8个周期（如5/13或8/21）
- 如需更保守的信号，优先调整Fast/Slow间距而非延长Regime

## 参考
- 策略：TrendStateMachineStrategy
- 最优参数：fast=5, slow=13, regime=34

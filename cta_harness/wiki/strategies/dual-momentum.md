# Dual Momentum 双动量策略

**状态**: ✅ Retain（接近毕业）
**代码**: `strategies/dual_momentum_strategy.py`
**类名**: `DualMomentumStrategy`
**来源**: [Dual Momentum on Bitcoin](../sources/dual-momentum-bitcoin.md)

## 设计思路

基于 Gary Antonacci 的 Dual Momentum（双动量）框架，适配比特币单标的 CTA 交易。

核心机制：
- **绝对动量**: close > SMA(200) on 4h — 判断长期趋势方向
- **相对动量**: ROC(50) > 0 on 4h — 判断近期趋势强度
- 双条件同时满足 → 入场做多
- 仅 ATR(20)×4.0 追踪止损离场
- 离场后 20 bar 冷却期避免 whip-saw
- 动态仓位: `max(1, int(capital/ATR × 0.007))`
- 仅做多（Long-Only）

## 最优参数

```
momentum_period = 200     # 4h SMA ≈ 33天趋势
roc_period = 50           # 4h ROC ≈ 8天动量
atr_period = 20           # ATR 周期
atr_stop_mult = 4.0       # 追踪止损宽度
bar_interval_minutes = 240  # 4h K线
cooldown_bars = 20        # 离场冷却 ≈ 3.3天
use_dynamic_size = True   # 动态仓位
position_multiplier = 0.007  # 仓位乘数
```

## 回测结果

### BTCUSDT.BINANCE (2019-2026)

| 指标 | slippage=0 | slippage=1 |
|------|-----------|-----------|
| Sharpe | 1.002 | 0.998 |
| 总收益 | 151.6% | 151.2% |
| 最大回撤 | -15.2% | -15.3% |
| 交易次数 | 272（~40次/年） | 272 |

### BNBUSDT.BINANCE (2020-2026)

| 指标 | 值 |
|------|-----|
| Sharpe | 0.872 |
| 总收益 | 131.5% |
| 最大回撤 | -11.0% |
| 交易次数 | 252 |

### 稳健性验证

| 分段 | Sharpe | 收益 | 结论 |
|------|--------|------|------|
| 前半段 (2019-2022) | 0.898 | +63.7% | ✅ 正收益 |
| 后半段 (2023-2026) | 0.907 | +50.2% | ✅ 正收益 |

## 关键教训

1. **v1 教训**: 1h 线上逐 bar 判断 + SMA 离场 → 过度交易（4074笔），手续费吞噬利润
2. **v2 核心改进**: 4h K线 + 去掉 SMA 离场 + 冷却期 → 交易降至 272 笔
3. **动态仓位胜负手**: 固定 Sharpe 0.47 → 动态 Sharpe 1.00（+113%）
4. **滑点免疫**: 4h K线 + 宽止损使策略对 1 tick 滑点几乎不敏感
5. **BNB 待优化**: 当前 BNB Sharpe 0.872，调整 position_multiplier 有望突破 1.0

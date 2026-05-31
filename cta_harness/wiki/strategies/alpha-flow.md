# AlphaFlow 波动率包络策略

**来源**: 20:00 cron 自主开发  
**状态**: retain

## 核心逻辑

```
信号:  HLC/3均价 → 双EMA(20/50)取均值 = baseline
通道:  baseline ± vol_multiplier × ATR
入场:  收盘价突破upper → 买入(体制翻转)
离场:  ① 收盘价 < lower
       ② close < EMA200(方向过滤)
       ③ ATR移动止损 trailing = close - 3×ATR
仓位:  fixed=1 或 dynamic = capital/ATR × multiplier
```

## 回测结果 (BTCUSDT 1h, 2020-2026)

| 版本 | Sharpe | 收益 | MaxDD | 交易 |
|------|:------:|------|------:|-----:|
| 固定仓位 | 0.45 | +22.2% | -7.3% | 520 |
| 动态仓位(0.005) | **0.73** | +30.1% | -8.4% | 196 |

## 稳健性

- 滑点测试(slip=1): Sharpe 0.455→0.449 ✅ 几乎无衰减
- 前半段(2020-2023): Sharpe 0.59, +12.2%
- 后半段(2023-2026): Sharpe 0.33, +9.4%

## 优化方向

- 加做空逻辑(对称bear regime)
- 波动率仓位已实现(动态版Sharpe 0.73)
- 入场确认(连续N根bar突破)

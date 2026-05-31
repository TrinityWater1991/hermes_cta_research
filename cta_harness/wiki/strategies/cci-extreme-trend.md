# CCI Extreme Trend Strategy

**状态:** ✅ Retain  
**核心逻辑:** CCI(14) ±300 极端值趋势跟踪，1h K线，ATR 移动止损

## 策略来源

Andrea Unger 在 Gold futures (COMEX) 上验证的 CCI 趋势跟踪思路：反直觉使用 CCI 作为趋势跟踪工具（±300 极端阈值），而非传统的均值回归工具。

## 设计要点

- BarGenerator 合成 1h K线（从 1m）
- CCI(14) 上穿 +300 → 做多 / 下穿 -300 → 做空
- CCI 回归 0 → 离场
- ATR(14)×3 移动止损保护

## 回测结果 (BTCUSDT.BINANCE, 2019-2026)

| 测试 | Sharpe | 收益 | MaxDD | 交易 |
|------|--------|------|-------|------|
| 基准(slip=0) | 0.623 | +20.6% | -3.96% | 820 |
| 滑点=1 | 0.610 | +20.2% | -3.98% | 820 |
| 前半段 | 0.663 | +8.9% | -3.27% | 410 |
| 后半段 | 0.600 | +11.7% | -4.29% | 410 |

## 决策

**Retain**。策略极其稳健（滑点几乎无影响，分段正收益），但 Sharpe 未达毕业标准 1.0。适合作为组合中的低相关性子策略。

## 文件

- 策略代码: `strategies/cci_extreme_trend_strategy.py`
- 研究目录: `research/2026-05-31_unger-gold-trend-following/`

# Keltner Channel Breakout 研究项目

**日期**: 2026-05-22
**来源**: [PyQuantLab - Keltner Channel Breakout Strategy](https://pyquantlab.com/article.php?file=Keltner+Channel+Breakout+Strategy+with+Optimization+and+Rolling+Backtest+Analysis.html)
**状态**: ✅ 已关闭 (Retain)

---

## 最终结论

**决策：Retain** — Keltner通道突破策略整体可用但未达毕业标准。滑点调整后最佳Sharpe(0.61 on jm99)低于毕业线1.0，且分段测试显示性能随时间衰减严重（i99前半Sharpe=1.06 vs 后半0.39）。

### 最终结果

| 品种 | Sharpe(滑=0) | Sharpe(滑=1) | 年化收益 | MaxDD | 交易次数 |
|------|:----------:|:----------:|:-------:|:-----:|:-------:|
| **rb99.SHFE** | 0.59 | **0.51** | +2.5% | -4.6% | 388 |
| **j99.DCE** | 0.59 | **0.50** | +20.1% | -23.5% | 397 |
| **i99.DCE** | 0.76 | **0.45** | +8.5% | -9.2% | 389 |
| **jm99.DCE** | 0.71 | **0.61** | +14.4% | -16.2% | 393 |

### Key Findings

1. **ATR周期参数无效**：Keltner通道的ATR周期(7-21)对结果几乎无影响
2. **滑点敏感度中等**：滑点=1下Sharpe平均下降0.15-0.31（约20-40%）
3. **时段不一致**：前半段Sharpe=1.06大幅优于后半段0.39
4. **交易频率合理**：年均~77次
5. **jm99表现最优**：滑点=1下Sharpe=0.61

### 教训

- Keltner通道突破策略在中国商品期货上有效但边缘，Sharpe在0.45-0.61区间
- ATR周期参数对此策略无效（因策略使用收盘价穿越通道，非盘中实时突破）
- 1h K线的Keltner通道信号低频但稳定，适合作为组合中的趋势暴露部分

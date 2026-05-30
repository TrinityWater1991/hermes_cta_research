# 时间序列动量（TSMOM）研究

**状态**: ❌ 已关闭（预验证失败）

**来源灵感**: [Improved TSMOM on Commodities Futures](wiki/sources/improved-tsmom-commodities-futures.md)
基于 Baltas & Kosowski "Demystifying Time-Series Momentum Strategies" 论文

---

## 结论

**预验证失败，未进入策略开发阶段。**

t-stat TSMOM信号在中国商品期货日线上的统计显著性极弱：
- 全部16个试验组合中，方向准确率均≤52%
- 唯一正Sharp的i99(lb=252, Sharpe=0.39)在2022年后衰减严重
- 简单TSMOM表现更差

教训：中国商品期货的趋势持续性弱于海外市场，学术TSMOM效应在此市场不显著。

---

**创建日期**: 2026-05-22
**关闭日期**: 2026-05-22

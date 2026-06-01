# I Built a Dual Momentum Strategy That Made 72.72% on Bitcoin With Only 3.86% Drawdown

**来源**: [Trading & Investing Strategies (Substack)](https://tradinginvestingstrategies.substack.com/p/i-built-a-trading-strategy-that-made)
**日期**: 2026-05-30
**作者**: Trading & Investing Strategies

## 核心理念

策略不预测精确入场点或顶部，只回答一个问题：**这个市场现在值得参与吗？**

基于 Gary Antonacci 的 Dual Momentum 框架：
1. **Absolute Momentum（绝对动量）** — 资产是否比之前更强？
2. **Relative Momentum（相对动量）** — 资产是否比防御性基准（如现金/短期债券）更强？

两个过滤器结合，确保只在资产"值得冒险"时持有多头仓位。

## 策略特点

- 纯做多 Long-only
- 增加趋势结构逻辑和再入场信号
- ATR 追踪止损出场
- 非曲线拟合：同样逻辑在 BTC、Gold、SPY 上均有效

## 回测结果（TradingView）

| 资产 | 收益 | 最大回撤 | 盈亏比 |
|------|------|---------|--------|
| BTCUSDT | 72.72% | 3.86% | 5.164 |
| Gold | 18.61% | 1.82% | 3.237 |
| SPY | 9.23% | 2.20% | 2.074 |

## 与传统均线系统的区别

大多数均线规则是二元的（价格在线上→买，线下→卖），在震荡市中频繁被割。Dual Momentum 增加第二层过滤：检查资产是否有实际动量，然后与防御性基准比较。因此系统不会交易每一个小的向上波动，而是隔离出"真正值得投入资本"的时刻。

## 学术基础

- [Risk Premia Harvesting Through Dual Momentum](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2042750) — Antonacci
- [Time Series Momentum](https://www.sciencedirect.com/science/article/pii/S0304405X11002613) — Moskowitz, Ooi, Pedersen
- [A Century of Evidence on Trend-Following Investing](https://fairmodel.econ.yale.edu/ec439/hurst.pdf) — Hurst, Ooi, Pedersen

## 注意

完整交易规则和 PineScript 代码需付费订阅。本文基于 Gary Antonacci 公开框架 + 文章描述的策略特征进行逆向工程实现。

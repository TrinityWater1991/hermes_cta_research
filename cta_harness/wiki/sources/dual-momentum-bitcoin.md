# Dual Momentum on Bitcoin（比特币双动量策略）

**来源**: [Trading & Investing Strategies (Substack)](https://tradinginvestingstrategies.substack.com/p/i-built-a-trading-strategy-that-made)
**作者**: Trading & Investing Strategies
**日期**: 2026-05-30

## 摘要

基于 Gary Antonacci 的 Dual Momentum（双动量）框架，构建比特币纯做多趋势策略。核心逻辑：同时使用绝对动量（价格是否在N日均线之上）和相对动量（近期收益是否为正/超过基准）两个过滤器，仅在两者同时满足时持仓。配合 ATR 追踪止损退出。

## 关键思路

1. **双过滤器设计**：绝对动量判断趋势方向，相对动量判断趋势强度，只有两者都通过才入场
2. **纯做多**：加密市场天然适合做多（长期牛市），规避做空假突破
3. **ATR 追踪止损**：代替固定均线交叉出场，让利润奔跑
4. **跨资产稳健**：同一逻辑在 BTC（72.72%）、Gold（18.61%）、SPY（9.23%）上均有效

## 潜在策略方向

1. **经典双动量版 (v1)**：SMA(N) + 返回率>0 双过滤，ATR 追踪止损
2. **动态仓位版 (v2)**：在 v1 基础上增加 capital/ATR 仓位缩放
3. **多周期确认版 (v3)**：日用双周期绝对动量确认，减少假信号

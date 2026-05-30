# Royal Purple Trend State Machine

## 来源
Royal Purple Dual Asset Trend Follower — Trading & Investing Strategies (Discole), 2026-05-05

## 核心思路
将趋势跟踪视为状态机：趋势是持续状态而非事件信号。
三层EMA（Fast/Slow/Regime）确认趋势状态，自适应移动止损，被止损后若趋势仍存则重入场。

## 提取的策略方向
1. **三层EMA趋势状态机 v1** — 基础版本，已实现并回测
2. **趋势状态+通道突破 v2** — 未测试
3. **自适应移动止损变体 v3** — 未测试

## 研究结果
- **状态**: 已关闭（Retain）
- **最佳品种**: jm99.DCE（焦煤）
- **最优参数**: fast_ema=5, slow_ema=13, regime_ema=34
- **最佳结果**: Sharpe 0.78（slippage=0）/ 0.66（slippage=1）
- **最佳区间**: 2021-2023上半段（Sharpe 0.97+）
- **主要局限**: 2023年后效应衰减，仅jm99表现稳定

## 关键教训
1. 三层EMA趋势状态机效果依赖"层间距"：Fast/Slow/Regime的间距远比绝对值重要
2. 在1小时K线上，快参数（5/13/34）比保守参数（8/21/55）更好
3. 趋势反转离场（反手）比纯止损离场能更好捕获大趋势
4. 重入场机制（冷却期控制）能减少被假突破清洗后的踏空

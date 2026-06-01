# Mulvaney Donchian 趋势跟踪 — 研究项目

**目录**: `research/2026-06-01_mulvaney-donchian-pyramiding/`
**来源文章**: [You Can Trade (Almost) Like Mulvaney](https://concretumgroup.substack.com/p/you-can-trade-almost-like-mulvaney) (Concretum Group, 2026-05-02)
**状态**: ✅ Retain（BTC Sharpe 1.02，待 BNB 优化后重新评估毕业）

## 策略概述

逆向工程 Paul Mulvaney 的 26 年长线趋势跟踪系统，适配加密单标的。核心机制：
- Donchian 通道突破入场（2h K线）
- 固定初始止损（通道宽度 × offset）
- Donchian 中线追踪止损（单向移动）
- 动态仓位（capital/ATR × multiplier）
- 仅做多（加密长期牛市偏向）

## 研究方向

1. **MulvaneyTrendStrategy** — 简化版：Donchian 突破 + 固定止损 → 中线追踪止损
2. 金字塔加仓版（v2，如果基础版有效）
3. 多周期 Donchian 变体（200/300/500 bar）

## 回测参数

| 参数 | 值 |
|------|-----|
| 合约 | BTCUSDT.BINANCE |
| K线周期 | 2h（BarGenerator 从 1m 合成） |
| 回测区间 | 2019-09-01 ~ 2026-06-01 |
| capital | 200,000 |
| size | 1 |
| pricetick | 0.01 |
| rate | 0.0004 |
| slippage | 0（初始）→ 1（稳健性） |

## 预期

- 交易频率低（年均 5-15 次）
- 依赖 BTC 长期上升趋势
- 需动态仓位提升 Sharpe

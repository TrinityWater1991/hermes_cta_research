# Keltner Channel Breakout 策略

**来源**: [PyQuantLab - Keltner Channel Breakout Strategy: Optimization & Rolling Backtest Analysis](https://pyquantlab.com/article.php?file=Keltner+Channel+Breakout+Strategy+with+Optimization+and+Rolling+Backtest+Analysis.html)

**日期**: 2025

## 核心思想

Keltner 通道突破策略是一种基于波动率的趋势跟踪策略。当价格突破 Keltner 通道上轨/下轨时入场，当价格回归 EMA 中轨时离场。

### Keltner 通道构成

- **中线（mid）**: 收盘价的 EMA
- **上轨（top）**: mid + (ATR × multiplier)
- **下轨（bot）**: mid - (ATR × multiplier)

### 交易逻辑

**做多入场**: 前一周期收盘价 > 前一期上轨（向上突破）
**做空入场**: 前一周期收盘价 < 前一期下轨（向下突破）
**做多离场**: 当前收盘价 < 当前 EMA 中轨（回归均值）
**做空离场**: 当前收盘价 > 当前 EMA 中轨（回归均值）

### 参数

- `ema_period`: [20, 30, 40, 50]
- `atr_period`: [7, 14, 21]
- `atr_multiplier`: [0.5, 1.0, 1.5, 2.0, 2.5]

## 关键特点

1. 使用 EMA 而非 SMA 作为中轨，对价格变化更敏感
2. 离场逻辑是回均值（EMA），而非反向突破，减少假信号
3. 通道宽度由 ATR 动态调整，适应不同波动率环境
4. 优化结果在 BTC 上 Sharpe=1.11（EMA=50, ATR=14, mult=2.0）

## 与已有策略的差异

- 不同于 Turtle Trading（Donchian 突破）：Keltner 通道基于 ATR 宽度而非历史最高最低
- 不同于 Concretum Intraday ATR（日内开盘价通道）：本策略是趋势跟踪，非日内回归
- 不同于 Concretum Dual Channel（Donchian+EMA 过滤）：本策略通道本身就是 ATR 宽度，离场是回归 EMA 而非反向通道突破
- 不同于 MultiMaTrend（多周期 MA 因子）：本策略使用单一 EMA 中轨 + ATR 通道

## 潜在研究方向

1. **基础 Keltner 通道突破** — 突破上下轨入场，回归 EMA 离场
2. **多时间框架 Keltner** — 长周期过滤方向，短周期执行突破
3. **ADX 过滤版** — ADX > 25 时启用突破信号，避免盘整期假突破
4. **波动率目标版** — 根据 ATR 调整仓位大小

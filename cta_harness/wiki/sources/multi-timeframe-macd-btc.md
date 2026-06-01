# Multi-Timeframe MACD Trend Strategy on Bitcoin

**来源**: [Quantpedia](https://quantpedia.com/how-to-design-a-simple-multi-timeframe-trend-strategy-on-bitcoin)
**作者**: David Mesíček, Junior Quant Analyst, Quantpedia
**日期**: 2025

## 摘要

文章从零开始，逐步构建一个系统化的比特币做多趋势跟踪策略。核心理念来自 Alexander Elder 的《Come Into My Trading Room》：在更高时间框架确定主趋势方向，然后在较低时间框架寻找精确入场点。

### 策略演进三个版本

1. **纯 MACD 交叉 (1H 基准)**：MACD 金叉做多，死叉平仓。Sharpe 0.33，年化 4.6%，最大回撤 -23.9%，2262 笔交易。

2. **D1H1 过滤 (改进入场)**：只在日线 MACD 金叉（主趋势向上）时才接受 1H 做多信号。Sharpe 0.80，年化 6.6%，最大回撤 -12.4%，约 1000 笔交易。

3. **D1H1 STOP (最终版)**：增加价格行为追踪止损——持仓后，直到出现第一根阴线（close < open）时平仓。进一步改善回撤和稳定性。

### 关键发现

- 多层逻辑（多时间框架确认 + 自适应出场）比参数优化更重要
- 多时间框架确认大幅减少假信号和回撤
- 价格行为出场（首根阴线平仓）透明、稳健、避免过拟合
- 仅做多是合理选择，因比特币长期上涨趋势

## 策略方向

1. **基础版**: 1H MACD 交叉 + D1 MACD 趋势过滤，固定持仓（1根K线后平仓）
2. **追踪止损版**: 同上入场 + 价格行为追踪止损（首根阴线出场）
3. **ATR 止损版**: 同上入场 + ATR 移动止损替代价格行为出场
4. **动态仓位版**: 增加波动率调整仓位（capital/ATR × multiplier）

## 最终结论（2026-06-01）

**Discard**。6个策略变体在 BTCUSDT.BINANCE (2019-2026) 上 Sharpe 均 < 0。MACD 在 1H 上的信号翻转频率远低于原文声称值（65次 vs 2262次），信号不具备预测能力。原文结果可能源于不同参数、不同数据源（Gemini vs Binance）或不同统计口径。

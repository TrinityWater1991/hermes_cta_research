# Multi-Timeframe MACD BTC 研究

**来源**: Quantpedia "How to Design a Simple Multi-Timeframe Trend Strategy on Bitcoin"
**日期**: 2026-06-01
**状态**: ❌ 已淘汰

## 最终结论

**Discard**。MACD 信号在 BTCUSDT.BINANCE 1H 数据上无 alpha。

6 个变体回测，Sharpe 均 < 0：
- MACD(12,26,9) 交叉: 31笔, Sharpe -0.23
- 更快 MACD(5,15,5): 97笔, Sharpe -0.23
- 动态仓位: 爆仓

MACD 在 1H 上翻转频率远低于原文声称值，信号在 7 年 BTC 历史中不具备预测能力。

# I paper-traded 22 popular crypto strategies on real fees

**来源**: Quantocracy → StratProof  
**原文**: https://stratproof.com/blog/paper-trading-22-strategies-real-fees  
**入库日期**: 2026-05-31

## 核心教训

在 Binance 实盘费率（往返 0.25-0.30%）下跑了 22 个策略 10 天：

| 类型 | 盈利/总数 | 结论 |
|------|:--------:|------|
| RSI 均值回归 | 6/6 盈利 | 短线 MR 每笔赚 0.05-0.20%，刚好够覆盖费率 |
| 趋势跟踪 | 0/16 盈利 | MACD/Supertrend/EMA Cross 全灭，费率是杀手 |

**关键数据：**
- 26,765 笔交易，胜率 32.6%，累计亏损 -2,081%
- EMA Cross (31% 胜率) 无法覆盖 0.25% 费率 → 缓慢失血
- 1h/4h/日线 周期越长越惨（费率占比越大）
- 只有 BTC/ETH/SOL/BNB/XRP/DOGE 前 6 币种勉强打平

**教训：**
- 零费率回测是最大的谎言
- 参数多样性 ≠ 信号多样性（6 个"不同"RSI 策略实际只有 1.2 个有效策略）
- 加"山寨币做分散化"实际上通过点差摧毁收益

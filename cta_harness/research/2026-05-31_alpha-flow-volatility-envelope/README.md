# Alpha Flow 波动率包络策略研究

**来源:** [wiki/sources/alpha-flow-volatility-envelope.md](../../wiki/sources/alpha-flow-volatility-envelope.md)
**日期:** 2026-05-31
**状态:** ❌ 已淘汰

## 研究方向

1. **Alpha Flow 基础版 (v1)**: 双EMA基线 + 波动率包络 + 收盘价体制锁定 → 未单独测试，直接在v2中实现
2. **EMA方向过滤版 (v2)**: 增加长期EMA确保只在主趋势方向交易 → 已测试，Sharpe=0.07
3. **做多做空双向版 (v3)**: 未开发

## 回测结果

- 合约: BTCUSDT.BINANCE
- 数据: 2019-09-17 → 2026-05-30 (1m K线)
- 5个参数变体，最优 Sharpe=0.07

## 最终结论

**Discard**。双EMA(HLC/3)基线 + ATR波动率包络 + 收盘价体制锁定在BTC上无alpha。所有变体Sharpe < 0.1，核心原因：

1. ATR包络在加密高波环境下无法区分趋势与噪音
2. 体制锁定 + ATR止损组合导致"最大回撤吸收所有利润"
3. 0.08%往返手续费在微薄利润上致命

详见 [iterations.md](iterations.md) 和 [wiki/lessons/alpha-flow-envelope-crypto.md](../../wiki/lessons/alpha-flow-envelope-crypto.md)。

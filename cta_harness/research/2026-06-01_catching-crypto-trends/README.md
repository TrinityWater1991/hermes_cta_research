# Catching Crypto Trends 研究项目

**来源**: [wiki/sources/catching-crypto-trends.md](../../wiki/sources/catching-crypto-trends.md)
**日期**: 2026-06-01
**状态**: 🔄 Retain — slippage=1 Sharpe=0.48, 盈利+稳健但未达毕业标准

## 研究方向

1. **Donchian Ensemble (核心版) v1**: 日线 5-lookback Donchian ensemble + ATR动态仓位 + DonchianMid追踪止损 ✅ 已实现

## 回测参数

- 合约: BTCUSDT.BINANCE
- 数据: 2019-09-17 ~ 2026-05-30 (1m → 日线BarGenerator合成)
- capital: 200,000, size=1, pricetick=0.01, rate=0.0004

## 最终结果

| 指标 | slip=0 | slip=1 | 前半段 | 后半段 |
|------|:------:|:------:|:------:|:------:|
| Sharpe | 0.477 | 0.477 | 0.501 | 0.429 |
| 总收益 | +66.8% | +66.7% | +39.6% | +21.3% |
| MaxDD | -25.4% | -25.4% | -25.4% | -12.4% |
| 交易数 | 162 | 162 | 92 | 62 |

**最优参数**: dc=[3,10,30,90,200], entry_threshold=0.3, position_multiplier=0.007, use_dynamic_size=1

## 结论

策略盈利且稳健（滑点免疫、分段均正），但 Sharpe 仅 0.48，远低于论文报告的 1.5。差距归因于：
1. 论文使用 2015 年起的完整 BTC 数据（含 2017 超级牛市），我们仅从 2019 年开始
2. 论文的 9-lookback 集成 + 波动率目标仓位管理在单标的实现中效果打折
3. 日线频率在 BTC 上信号稀疏（162 笔/6.7 年），限制了 alpha 积累

策略代码保留，作为 Donchian 集成+追踪止损的参考实现。未来方向：4h 版本、论文原始 vol targeting、BNB 跨品种验证。

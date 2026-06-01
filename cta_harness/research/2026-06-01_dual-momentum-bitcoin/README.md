     1|# Dual Momentum Bitcoin 研究项目
     2|
     3|**来源**: [wiki/sources/dual-momentum-bitcoin.md](../../wiki/sources/dual-momentum-bitcoin.md)
     4|**日期**: 2026-06-01
     5|**状态**: 🔄 Retain（BTC Sharpe 1.002 ✅，BNB 0.872 无法突破1.0 ❌，ETH数据不足，缺第二合约验证）
     6|
     7|## 研究方向
     8|
     9|1. **经典双动量版 (v1)**: SMA(N) 绝对动量 + 收益率>0 相对动量，ATR追踪止损，纯做多
    10|2. **动态仓位版 (v2)**: v1 + capital/ATR 动态仓位缩放
    11|3. **多周期确认版 (v3)**: 日线+小时线双周期确认
    12|
    13|## 回测参数
    14|
    15|- 合约: BTCUSDT.BINANCE
    16|- 数据: 2019-2026 1m K线
    17|- K线合成: 1h (BarGenerator)
    18|- capital: 200,000
    19|- size: 1
    20|- pricetick: 0.01
    21|- rate: 0.0004
    22|- slippage: 0 → 1
    23|
    24|## 预期
    25|
    26|双动量过滤器应减少假突破，配合 ATR 追踪止损实现高盈亏比低回撤。
    27|

## 最终结果

### 最优参数

```
momentum_period=200 (4h SMA ≈ 33天)
roc_period=50 (4h ROC ≈ 8天)
atr_period=20
atr_stop_mult=4.0
bar_interval_minutes=240 (4h K线)
cooldown_bars=20 (冷却期 ≈ 3.3天)
use_dynamic_size=1
position_multiplier=0.007
```

### BTCUSDT 回测 (2019-2026)

| 指标 | slippage=0 | slippage=1 |
|------|-----------|-----------|
| Sharpe | 1.002 | 0.998 |
| 总收益 | 151.6% | 151.2% |
| 最大回撤 | -15.2% | -15.3% |
| 交易次数 | 272 | 272 |
| 手续费 | $9,081 | $9,081 |
| 滑点成本 | $0 | $952 |

### BNBUSDT 回测 (2020-2026)

| 指标 | 值 |
|------|-----|
| Sharpe | 0.872 |
| 总收益 | 131.5% |
| 最大回撤 | -11.0% |
| 交易次数 | 252 |

### 决策: Retain

策略 BTC 单独达标所有毕业标准（Sharpe 1.002, MaxDD -15.2%, 272 Trades），但 BNB 最优 Sharpe 仅 0.872（2026-06-01 优化尝试未突破），ETHUSDT 数据不完整。缺第二合约验证，无法毕业。代码保留，待数据补全或其他品种测试。

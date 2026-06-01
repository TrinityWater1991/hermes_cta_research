# Donchian 集成趋势跟踪（Catching Crypto Trends）

**来源**: Concretum Group (2025), SSRN 5209907
**实现**: strategies/donchian_ensemble_strategy.py
**状态**: 🔄 Retain

## 策略逻辑

日线 Donchian close 通道集成趋势跟踪。5 个不同回溯期的 Donchian 通道等权投票产生入场信号，DonchianMid 单向追踪止损管理持仓。

### 入场
- 5 个 Donchian close 通道各产生二值信号（close ≥ DonchianUp）
- Ensemble 信号 = 各模型"突破"的等权比例
- Ensemble ≥ entry_threshold (0.5) → 入场

### 离场
- DonchianMid（最长 lookback 360 的中线）单向追踪止损
- 只在 DonchianMid 上移时更新，从不下移
- 入场日初始止损 = 激活模型的 DonchianMid 均值
- close ≤ trailing stop → 离场

### 仓位管理
- 动态: size = max(1, int((200000/ATR) × position_multiplier))

## 回测（BTCUSDT.BINANCE, 2019-2026）

| 参数 | 值 |
|------|-----|
| K线 | 日线 |
| Lookback | [3, 10, 30, 90, 200] |
| 入场所需 | ≥ 0.3 (1-2 个模型) |
| 仓位乘数 | 0.007 |

| 指标 | slip=0 | slip=1 |
|------|:------:|:------:|
| Sharpe | 0.48 | 0.48 |
| 总收益 | +66.8% | +66.7% |
| MaxDD | -25.4% | -25.4% |
| 交易数 | 162 | 162 |

## 结论

策略盈利+稳健（滑点免疫、分段均正），但 Sharpe 未达毕业标准。论文报告 Sharpe>1.5 但覆盖 2015 年起的完整 BTC 牛市，2019-2026 缺乏该效应。保留代码。

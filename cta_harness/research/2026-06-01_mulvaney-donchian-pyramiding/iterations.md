# 迭代记录

## v1 — 初始版本 (2026-06-01)

**策略**: MulvaneyTrendStrategy
**核心逻辑**:
- 2h K线（BarGenerator + Interval.HOUR），Donchian 通道突破入场（仅做多）
- 初始固定止损：通道宽度 × stop_offset（默认 0.33）
- 追踪止损切换：价格突破入场价 + 通道宽度后切换为中线追踪
- 动态仓位：max(1, int(200000 / ATR × position_multiplier))
- Donchian 中线单向移动追踪止损

**关键bug修复**:
- Donchian 计算排除当前 bar（否则 close ≤ high 永远不触发）
- BarGenerator 60+分钟窗口必须用 Interval.HOUR（vnpy 限制：MINUTE 仅支持整除 60 的窗口）

**回测结果** (donchian_period=100, pm=0.005, dynamic_size=true):

| 合约 | Sharpe | Return | MaxDD | Trades |
|------|:------:|:------:|:-----:|:------:|
| BTCUSDT (slip=0) | **1.02** | +134.9% | -8.73% | 232 |
| BTCUSDT (slip=1) | **1.02** | +134.5% | -8.77% | 232 |
| 前半段 2019-2022 | **1.01** | +64.3% | -8.73% | 106 |
| 后半段 2023-2026 | **1.04** | +72.7% | -7.99% | 122 |
| BNBUSDT (slip=0) | **0.64** | +181.4% | -19.96% | 234 |

**决策**: Retain — BTC 表现优异（Sharpe 1.02, 滑点免疫），但 BNB Sharpe 仅 0.64 < 1.0，未达毕业标准（需2合约均 Sharpe≥1.0）。BNB 参数未优化（direct port），需独立调参。

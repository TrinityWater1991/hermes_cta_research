# MulvaneyTrendStrategy — Donchian 中线追踪止损

**状态**: 🔄 Retain（待 BNB 参数优化后重新评估毕业）
**来源**: [You Can Trade (Almost) Like Mulvaney](https://concretumgroup.substack.com/p/you-can-trade-almost-like-mulvaney)
**研究项目**: `research/2026-06-01_mulvaney-donchian-pyramiding/`

## 核心逻辑

逆向工程 Paul Mulvaney 的 26 年长线趋势跟踪系统，适配加密单标的：
1. **Donchian 通道突破入场**（2h K线，仅做多）
2. **固定初始止损**：通道宽度 × 0.33
3. **中线追踪止损**：Donchian 中线单向移动，浮盈达标后激活
4. **动态仓位**：max(1, int(200000 / ATR × 0.005))

## 回测结果

| 合约 | Sharpe | Return | MaxDD | Trades |
|------|:------:|:------:|:-----:|:------:|
| BTCUSDT sl=0 | **1.02** | +134.9% | -8.73% | 232 |
| BTCUSDT sl=1 | **1.02** | +134.5% | -8.77% | 232 |
| 前段 2019-22 | **1.01** | +64.3% | -8.73% | 106 |
| 后段 2023-26 | **1.04** | +72.7% | -7.99% | 122 |
| BNBUSDT sl=0 | **0.64** | +181.4% | -19.96% | 234 |

## 关键发现

1. **滑点免疫**：低交易频率（~35次/年）使滑点成本可忽略
2. **分段一致**：前后段 Sharpe 1.01/1.04，无效应衰减
3. **动态仓位关键**：固定仓位下 Sharpe 仅 0.02，动态仓位提升至 1.02
4. **BNB 需独立调参**：直接复用 BTC 参数 Sharpe 仅 0.64，MaxDD 接近 20%

## 技术要点

- vnpy BarGenerator: 60+ 分钟窗口必须用 `Interval.HOUR`（MINUTE 仅支持整除 60 的窗口）
- Donchian 计算必须排除当前 bar，否则 close ≤ high 永远不触发
- Donchian 100期 × 2h = 200h ≈ 8.3天，适合中期趋势

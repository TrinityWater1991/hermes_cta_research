# Catching Crypto Trends — Donchian集成趋势跟踪

**来源**: Concretum Group (2025-05-06)
**SSRN**: [5209907](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5209907)
**原始文件**: `raw/articles/2025-05-06_catching-crypto-trends.md`

## 摘要

将经典 Donchian Channel 突破趋势跟踪方法应用于加密市场。核心创新：**9 个不同回溯期的 Donchian 通道集成模型** + **波动率目标仓位管理** + **DonchianMid 追踪止损**。

BTC 2015-2025 回测：Sharpe > 1.5, CAGR 30%, MaxDD 19%。与 SG Trend Index 相关性仅 7.4%，提供与传统 CTA 的低相关性多元化。

## 策略方向

1. **Donchian Ensemble (核心版)**: 9-lookback 日线 Donchian ensemble + vol targeting + midpoint trailing stop
2. **精简集成版**: 3-5 个 lookback 周期，降低计算量和最小数据需求
3. **高频适配版**: 用 4h/1h K线替代日线，按比例缩放 lookback 周期
4. **固定仓位版**: 同上但固定仓位，作为 baseline 对比

## 回测参数

- 合约: BTCUSDT.BINANCE
- 数据: 1m K线 → 日线 BarGenerator 合成
- capital: 200,000
- rate: 0.0004, size: 1, pricetick: 0.01

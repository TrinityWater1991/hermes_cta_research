# CCI 极端值趋势跟踪策略研究

**来源:** [wiki/sources/unger-gold-trend-following.md](../../wiki/sources/unger-gold-trend-following.md)
**日期:** 2026-05-31
**状态:** 🚧 开发中

## 研究方向

### 方向1: CCI ±300 极端值趋势跟踪
将 Andrea Unger 的 CCI 极端值趋势跟踪策略移植到加密市场。

**原文逻辑:**
- CCI(period) 突破 ±300 入场
- CCI 回归零附近离场
- Gold futures COMEX 上验证有效，均利 >$200

**适配要点:**
- BTCUSDT.BINANCE 1h K线（使用 BarGenerator 合成）
- CCI 周期保持灵活（默认14，可调）
- 阈值可能需要根据加密波动率调整（250/300/350）
- 必须添加 ATR 移动止损（原文无止损？需验证）
- 做多做空双向

### 方向2: 日高低突破趋势跟踪
将前一日高/低作为突破水平的纯价格行为策略。

**适配要点:**
- 24×7 加密的"日"定义为 UTC 日线（BarGenerator 合成日K）
- 使用停止单（buy/sell）在日线高点之上/低点之下入场
- 固定 ATR 倍数止损/止盈
- 1h K线上触发，减少噪音

## 回测参数

```
合约: BTCUSDT.BINANCE
数据: 1m K线 → BarGenerator 合成 1h/日
capital: 200,000
size: 1
rate: 0.0004
pricetick: 0.01
slippage: 0
interval: 1m
```

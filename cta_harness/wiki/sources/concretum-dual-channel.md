# Concretum 双通道趋势过滤策略

**来源**: Concretum Group — "A Century of Profitable Industry Trends"
**论文**: SSRN 4857230

## 核心思路

同时使用唐奇安通道（Donchian Channel）和另一类通道（Keltner/ATR-based），取上轨的最小值、下轨的最大值作为"组合通道"入场信号。两个通道同时确认趋势才入场，减少假突破。

## 策略逻辑

1. **入场通道**: `long_band = min(donchian_upper, keltner_upper)` 为做多上轨，`short_band = max(donchian_lower, keltner_lower)` 为做空下轨
2. **入场条件**: 价格突破 long_band 做多，突破 short_band 做空
3. **离场逻辑**: ATR移动止损 + 反向通道突破
4. **附加过滤**: ATR波动率过滤

## 研究方向

1. **Donchian + Keltner 双重确认** — 原版思路（Concretum 方式）
2. **Donchian + EMA 斜率过滤** — 用EMA方向确认趋势，Donchian通道做精确入场
3. **Donchian + 趋势因子** — 结合 MultiMaTrend 的趋势因子做方向判断

## 回测参数

- 合约: rb99.SHFE / j99.DCE / i99.DCE / jm99.DCE
- 数据: 1分钟（BarGenerator合成1小时K线）
- rate=0.0001, slippage=0, capital=200,000
- 周期: 2021-01-01 ~ 2026-05-21

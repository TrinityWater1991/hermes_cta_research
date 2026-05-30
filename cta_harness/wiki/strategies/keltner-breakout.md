# KeltnerBreakout 策略

**状态：** 已产出 (Retain)
**最优 Sharpe：** 0.61 (jm99.DCE, slippage=1)

## 策略概述

Keltner 通道突破策略：使用 1h K线，价格突破 Keltner 通道（EMA中轨 + ATR上下轨）时入场，价格回归 EMA 中轨时离场。

来源：[PyQuantLab - Keltner Channel Breakout Strategy](https://pyquantlab.com/article.php?file=Keltner+Channel+Breakout+Strategy+with+Optimization+and+Rolling+Backtest+Analysis.html)

## 策略参数

| 参数 | 默认值 | 说明 |
|------|:------:|------|
| ema_period | 50 | Keltner通道EMA周期 |
| atr_period | 14 | ATR周期 |
| atr_multiplier | 2.0 | ATR倍数（通道宽度） |
| fixed_size | 1 | 交易手数 |

## 交易逻辑

### 入场
- **做多：** 收盘价上穿 Keltner 通道上轨（且无持仓时）
- **做空：** 收盘价下穿 Keltner 通道下轨（且无持仓时）
- 使用限价单（收盘价±5跳）

### 离场
- **多头：** 收盘价跌破 EMA 中轨
- **空头：** 收盘价站上 EMA 中轨
- 无止损/止盈，完全依靠通道回归机制

### 数据周期
- 输入：1分钟 K线
- 合成：1小时 K线（60分钟窗口）
- 指标：Keltner(ema_period, atr_multiplier), EMA(ema_period)

## 回测结果

### 默认参数 (ema=50, atr=14, mult=2.0)

| 品种 | Sharpe(0) | Sharpe(1) | 总收益 | 年化收益 | MaxDD | 交易次数 |
|------|:--------:|:--------:|:-----:|:-------:|:-----:|:-------:|
| **jm99.DCE** | 0.71 | **0.61** | +66.2% | +14.4% | -16.9% | 393 |
| **rb99.SHFE** | 0.59 | **0.51** | +11.1% | +2.5% | -4.8% | 388 |
| **j99.DCE** | 0.59 | **0.50** | +88.9% | +20.1% | -27.1% | 397 |
| **i99.DCE** | 0.76 | **0.45** | +26.8% | +8.5% | -13.7% | 389 |

### 最优参数 (i99: ema=40, mult=2.0)

| 测试 | Sharpe | 说明 |
|------|:-----:|------|
| 全期滑=0 | 0.82 | 参数优化后提升有限 |
| 全期滑=1 | 0.47 | 滑点敏感 |
| 前半段(2021-2023) | 1.06 | 强趋势期表现好 |
| 后半段(2023-2026) | 0.39 | 震荡期衰减严重 |

## 关键发现

1. **ATR周期参数无效**：Keltner通道的ATR周期(7-21)对结果几乎无影响，通道宽度仅由ATR倍数决定
2. **滑点敏感度中等**：滑点=1下Sharpe平均下降0.15-0.31
3. **时段不一致**：前半段Sharpe=1.06大幅优于后半段0.39
4. **交易频率合理**：年均~77次，非过度交易
5. **jm99表现最优**：滑点=1下Sharpe=0.61，在所有品种中最好

## 文件

- 策略代码：`strategies/keltner_breakout_strategy.py`
- 研究项目：`research/2026-05-22_keltner-channel-breakout/`

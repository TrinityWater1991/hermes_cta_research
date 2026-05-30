# ConcretumIntradayATRBreakout — 日内ATR通道突破

**状态**: 已产出（Retain）

**策略文件**: `strategies/concretum_intraday_atr_breakout_v1_strategy.py`

---

## 设计思路

基于 Concretum Group QuanTips #2：开盘价 ± 0.5×ATR(7) 构成日内通道，突破入场，回归开盘价离场，收盘前平仓。

## 回测结果

### rb99.SHFE（螺纹钢，1小时K线，2021-2026）

| 条件 | Sharpe | 收益 | MaxDD | 交易次数 |
|------|:-----:|:----:|:-----:|:-------:|
| slippage=0 | 0.68 | +12.3% | -3.4% | 4389 |
| slippage=1 | -0.57 | — | — | ⚠️完全崩溃 |

### 多品种（slippage=0）

| 品种 | Sharpe |
|------|:-----:|
| rb99.SHFE | 0.68 |
| j99.DCE | 0.00 (爆仓) |
| i99.DCE | -0.53 |
| jm99.DCE | -0.31 |

## 评估

- **仅rb99有效**：DCE合约上完全失效
- **滑点极端敏感**：1跳滑点Sharpe从0.68变为-0.57
- **结论**: 保留代码，标注为"零滑点策略"

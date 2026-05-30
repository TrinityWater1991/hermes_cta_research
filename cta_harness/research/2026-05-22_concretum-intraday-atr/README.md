# Concretum Intraday ATR Breakout 研究项目

**来源：** [Concretum Intraday ATR Breakout](../wiki/sources/concretum-intraday-atr-breakout.md)
**日期：** 2026-05-22
**状态：** ✅ 已关闭 (Retain)

---

## 最终结论

**决策：Retain** — 策略在 rb99 上零滑点下表现合格，但含滑点后完全崩溃。保留代码。

### 最终结果

| 品种 | Sharpe(滑=0) | Sharpe(滑=1) | 年化收益 | MaxDD | 交易次数 |
|------|:----------:|:----------:|:-------:|:-----:|:-------:|
| **rb99.SHFE** | **0.68** | **-0.57** | +12.3% | -3.4% | 4389 |
| j99.DCE | 0.00 (爆仓) | — | — | — | — |
| i99.DCE | -0.53 | — | -25.0% | -40.1% | 4362 |
| jm99.DCE | -0.31 | — | -25.6% | -60.0% | 4326 |

### 最优参数
- atr_period=7
- atr_multiplier=0.5
- 1小时K线（BarGenerator从1m合成）
- 入场：收盘价突破开盘价±0.5×ATR(7)通道
- 离场：价格回归开盘价 或 收盘前强制平仓

### 关键发现

1. **仅rb99有效**：DCE合约（j99/i99/jm99）上完全失效，爆仓或负收益
2. **滑点敏感**：零滑点Sharpe 0.68，1跳滑点直接崩溃至-0.57
3. **信号精度低但不对称性盈利**：Pre-validation显示信号方向准确率仅~40%，但持有至收盘的"EOD"子集有60-72%胜率，说明策略盈利来自少数大幅波动日
4. **买卖点密集**：年均~870次交易，交易成本高

### 教训
- **wiki/lessons/atr-channel-intraday-slippage.md** — 日内ATR通道策略滑点敏感度分析

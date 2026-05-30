# 迭代记录

## v1 — 经典海龟交易系统（1h K线适配版）

**日期：** 2026-05-22
**策略文件：** strategies/turtle_trading_strategy.py
**来源：** Rogue Quant — "I Backtested The Legendary Turtle Trading Strategy"

### 核心逻辑
- 1h K线合成（从1m数据）
- 20日Donchian通道突破入场（停止单）
- 10日Donchian反突破离场
- ATR移动止损（multiplier参数可调）
- 多空双向

### 决策: Retain

**最优参数:** entry_window=20, exit_window=10, atr_multiplier=2.0

| 品种 | Sharpe | 总收益 | 交易次数 | MaxDD |
|------|:-----:|:-----:|:-------:|:-----:|
| **i99.DCE** | **0.84** ✅ | +44.1% | 995 | -8.6% |
| jm99.DCE | 0.60 | +55.0% | 1026 | -9.0% |
| rb99.SHFE | 0.69 | +12.2% | 996 | -3.3% |
| j99.DCE | 0.49 | +71.4% | 1050 | -21.7% |

**判定依据:**
- ✅ 4品种全正收益，普适性好
- ✅ i99 Sharpe=0.84，接近毕业线
- ✅ 最大回撤可控（除j99外均<10%）
- ⚠️ 交易频率偏高（~200次/年）
- ⚠️ ATR止损几乎无效（与反突破离场逻辑重叠）

→ **Retain**: 经典策略适配后效果不错，但尚未达到毕业标准。

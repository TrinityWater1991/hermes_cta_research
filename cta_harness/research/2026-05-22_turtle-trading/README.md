# Turtle Trading Strategy 研究项目

**状态：** ✅ 已关闭 (Retain) | **日期：** 2026-05-22

## 来源
Rogue Quant Substack: "I Backtested The Legendary Turtle Trading Strategy Across 40 Futures Markets"

## 研究方向
### 方向1: 经典 Turtle 系统
- Donchian Channel(20) 突破入场
- Donchian Channel(10) 反向突破离场
- ATR 波动率仓位管理
- 2ATR 止损
- 多空双向

### 方向2: Turtle + EMA 趋势过滤
- EMA 20 斜率作为方向过滤
- 仅在大趋势方向上做突破入场

### 方向3: Turtle + ATR Trailing Stop
- 将 10日反突破离场改为 ATR trailing stop
- 更灵活的趋势捕捉

## 回测参数
- 品种: rb99.SHFE, j99.DCE, i99.DCE, jm99.DCE
- 周期: 1小时（日线备用）
- 滑点: 0（初始）/ 1（稳健性）
- 手续费: 0.0001
- 资金: 200,000

## 结论

**决策: Retain** | 日期: 2026-05-22

### 最优参数（全品种通用）
- entry_window=20, exit_window=10, atr_multiplier=2.0

### 回测结果（滑点=0）

| 品种 | Sharpe | 收益 | 交易次数 | MaxDD |
|------|:-----:|:---:|:-------:|:-----:|
| **i99.DCE** | **0.84** | +44.1% | 995 | -8.6% |
| jm99.DCE | 0.60 | +55.0% | 1026 | -9.0% |
| rb99.SHFE | 0.69 | +12.2% | 996 | -3.3% |
| j99.DCE | 0.49 | +71.4% | 1050 | -21.7% |

### 关键发现
1. **4品种全正收益** — 品种普适性好，无论在黑色系还是螺纹钢均有效
2. **i99 Sharpe=0.84 接近毕业线**，仅差0.16
3. **交易频率偏高**（~200次/年），可能在真实成本下承压
4. **atr_multiplier 参数几乎无影响** — ATR止损与反突破离场逻辑重叠，实际未生效
5. **entry_window 是唯一关键参数** — 20最佳，过长或过短均降低表现

### 状态
- [x] Ingest (2026-05-22)
- [x] Step 4: 信号显著性预验证
- [x] Step 5: Develop
- [x] Step 6: Backtest
- [x] Step 7: 诊断决策
- [x] Step 9: 毕业/保留/淘汰决策 → **Retain**

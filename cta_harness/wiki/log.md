# 操作日志

## [2026-05-31] retain | AlphaFlow v2 — 动态仓位 Sharpe 0.73 +30% -8.4%

## [2026-05-31] ingest | Alpha Flow Volatility Envelope — On-Chain Mind

波动率自适应双EMA趋势跟踪策略。核心创新：双EMA(HLC/3)基线 + 基线波动率包络(非价格ATR) + 收盘价体制锁定状态机。自2012年BTC数据134% CAGR。适配加密24x7天然特性。

## [2026-05-31] ingest | Rethinking Trend Following: Regime-Dependent Allocation — Quantocracy/Alpha Architect

## [2026-05-31] discard | Intraday Trend Trade Management — 3次回测全负 (最优 Sharpe -0.24)

## [2026-05-31] ingest | How to Manage an Intraday Trend Trade — Quantocracy/Concretum Group

## [2026-05-31] discard | Trend Following Replication — 3次回测全负 (最优 Sharpe -0.44)

## [2026-05-31] ingest | Trend Following (1/4): Replicating Your Own Program — Quantocracy/Beyond Passive

## [2026-05-19] backtest | 多品种批量回测（16合约×2策略）

在16个期货品种上测试IntradayMomentum和MultiMaTrend两个策略。
最优组合：
- MultiMaTrend on j99.DCE（焦炭）：Sharpe=0.95, Return=297.5%
- MultiMaTrend on ag99.SHFE（白银）：Sharpe=0.62, Return=148.6%
- MultiMaTrend on jm99.DCE（焦煤）：Sharpe=0.57, Return=98.3%
- IntradayMom on ag99.SHFE（白银）：Sharpe=0.60, Return=29.8%, MaxDD=-4.2%
配置已保存到output/configs/，报告已生成到output/reports/。

## [2026-05-19] close | Intraday Momentum研究项目

结论：Retain。Opening Range Breakout策略在slippage=0下Sharpe=0.74，分段测试均正收益，但未达毕业标准。效应2021年后衰减。代码保留。

## [2026-05-19] ingest | Intraday Momentum for ES and NQ

日内动量效应：开盘前半小时收益正向预测尾盘收益。学术研究已在中国商品期货（含钢材）上验证。研究方向：Opening Range Momentum、隔夜跳空延续、多时段确认。

## [2026-05-18] close | Coding Trend Factor研究项目

结论：策略可用但未达毕业标准。MultiMaTrendStrategy在slippage=1下Sharpe=0.47，能承受真实成本但不够优秀。保留代码。

## [2026-05-18] ingest | Coding Trend Factor

多周期MA加权趋势因子，原文为股票横截面因子，适配为单标的CTA趋势策略。研究方向：等权MA组合、三周期投票、自适应权重。

## [2026-05-18] close | Fast Trend Following研究项目

结论：Discard。策略在零滑点下Sharpe 1.0+，但加入1跳滑点后完全崩溃。
高频趋势跟踪思路不适合rb99（交易成本过高）。教训记录到wiki/lessons/slippage-trap.md。

## [2026-05-18] ingest | 策略设计模式提取

从8个参考策略中提取入场/离场/止损/仓位管理/代码规范模式，写入wiki/concepts/。

## [2026-05-18] ingest | VeighNa CTA核心API参考

从vnpy_ctastrategy源码提取ArrayManager、BarGenerator、CtaTemplate完整API，写入wiki/concepts/。

## [2026-05-17] init | 工作区初始化

创建CTA策略投研工作区目录结构，初始化wiki、模板和工具脚本。

## [2026-05-21] project | 项目结构优化

优化项：
- 删除过时文档 `raw/cta_workflow.md`（与 AGENTS.md 接口不一致）
- 参考策略从 `raw/strategies/` 迁移至 `references/strategies/`
- 孤立策略 `kalman_trend_strategy.py` 移入 `references/old/`
- 补齐 wiki/strategies/ 页面（multi-ma-trend, intraday-momentum）
- 4个空研究目录补写 README.md 标记待启动
- 创建 `.project_state.json` 记录项目全局状态
- 更新 AGENTS.md 目录结构

## [2026-05-21] ingest | Concretum Dual Channel

双通道趋势过滤（Donchian + Keltner 组合），从 Concretum Group 百年行业趋势论文适配为单品种CTA。研究方向：双重确认入场、EMA斜率过滤、趋势因子组合。

## [2026-05-21] close | Concretum Dual Channel — Retain

4个方向（v1/v2/v3 + 停止单版）共6个变体，全品种（rb99/j99/i99/jm99）测试。

最优版本 v2b（Donchian + EMA斜率，停止单入场）：
- jm99 Sharpe=0.96, i99 Sharpe=0.76, rb99 Sharpe=0.74, j99 Sharpe=0.38
- 分段测试两段均正（jm99: 1.13→1.32）
- 保留代码，jm99接近毕业标准

关键发现：
1. 1小时K线上必须用停止单捕获通道突破
2. 方向过滤（EMA斜率）比双重通道确认效果更好
3. 同样的策略在jm99和j99上表现差异大（品种特性影响显著）

## [2026-05-21] ingest | Royal Purple Trend State Machine

趋势状态机框架：三层EMA确认趋势状态（Fast/Slow/Regime），自适应移动止损，被止损后若趋势仍存则重入场。
适配方向：三层EMA趋势状态机、趋势状态+通道突破、自适应移动止损变体。

## [2026-05-22] backtest | TrendStateMachine v1 全品种回测 + 参数优化

默认参数回测4品种（rb99/j99/i99/jm99）：
- jm99 Sharpe=0.60最佳，其余Sharpe 0.39~0.58

参数优化（jm99上测试4种变体）：
- 最优: fast=5, slow=13, regime=34 → Sharpe **0.781**, Ret 96.9%
- 次优: fast=8, slow=21, regime=34, atr=3.5 → Sharpe 0.786

稳健性测试（最优参数，jm99）：
- slippage=1: Sharpe 0.658, Ret 80.1% ✓（能承受真实成本）
- 前半段: Sharpe 1.076→0.971（slippage=1）
- 后半段: Sharpe 0.397→0.203（slippage=1）⚠ 效应衰减明显

多品种slippage=1: jm99 0.658, j99 0.486, rb99 0.413, i99 0.155

## [2026-05-22] ingest | Improved TSMOM on Commodities Futures

相关性调整时间序列动量（t-stat信号+Yang-Zhang波动率+波动率目标仓位管理）。
研究方向：t-stat趋势信号、YZ波动率估计、波动率目标仓位。

## [2026-05-22] close | Trend State Machine — Retain

结论：Retain。策略在jm99上slippage=1下Sharpe 0.658>0.5，能承受真实成本。
效应2023年后衰减明显（后半段Sharpe仅0.20），未达毕业标准。
关键教训：三层EMA状态机在1h上信号延迟较大，更快EMA周期（5/13/34）比默认（8/21/55）更好。

## [2026-05-22] close | TSMOM研究项目 — 预验证失败

结论：Discard（未进入开发阶段）。t-stat TSMOM信号在中国商品期货上的预验证中，所有16个试验组合的方向准确率均≤52%。日频TSMOM效应在此市场不成立。教训记录到 wiki/lessons/tsmom-chinese-commodity.md。

## [2026-05-22] ingest | Larry Williams Smash Day Pattern

反趋势反转策略：Smash Day（突破失败日）后反向入场。8日回顾期效果最佳。源自Larry Williams著作。研究方向：基础Smash Day反转、趋势过滤版、波动率过滤版。

## [2026-05-22] close | Smash Day — Retain

结论：Retain。Smash Day 反转策略仅在 j99.DCE（焦炭）上有效。最优参数 lb=25, mult=2.0 下：
- 零滑点 Sharpe=0.49, 含滑点 Sharpe=0.44

分段测试（j99, 零滑点）：
- 前半段 (2021~2023): Sharpe=0.87 ✅
- 后半段 (2023~2026): Sharpe=-0.03 ❌

仅1个品种有效（rb99/i99/jm99均为负），效应2023年后完全衰减。保留代码。
## [2026-05-22] backtest | TurtleTrading 4品种全回测

默认参数 (entry=20, exit=10, mult=2.0) 滑点=0：

| 品种 | Sharpe | 总收益 | 交易次数 | MaxDD |
|------|:-----:|:-----:|:-------:|:-----:|
| **i99.DCE** | **0.84** | +44.1% | 995 | -8.6% |
| jm99.DCE | 0.60 | +55.0% | 1026 | -9.0% |
| rb99.SHFE | 0.69 | +12.2% | 996 | -3.3% |
| j99.DCE | 0.49 | +71.4% | 1050 | -21.7% |

参数扫描结论：
- i99 最优 entry=20（Sharpe 0.84），jm99 最优 entry=50（Sharpe 0.73）
- atr_multiplier 对结果几乎无影响（止损逻辑与通道离场重叠）
- 4品种均正收益，品种普适性好

## [2026-05-22] close | Turtle Trading — Retain

结论：Retain。经典海龟交易系统在1h K线上适配后，全品种正收益。i99 Sharpe=0.84 接近优秀，但交易频率偏高（~200次/年）。未达毕业标准但表现稳健，保留代码。

## [2026-05-22] graduate | TurtleTrading on i99.DCE 🎓

经典海龟交易策略适配版正式毕业！

**最终参数（2h K线）：** entry_window=6, exit_window=3, stop_multiplier=1.5, filter_ema_window=60
**i99.DCE 结果：** Sharpe=1.03, 总收益+50.1%, MaxDD=-5.0%, 729笔交易

迭代历程：
- v1: 1h双向 → i99 Sharpe=0.84
- v2: 纯ATR止损 → 0.82
- v3: 2h K线 → 0.83
- v4: +EMA60方向过滤 → 0.92
- v4 final: +stop_mult=1.5, entry=6 → **1.03** 🏆

关键成功因素：EMA单边方向过滤、激进ATR止损(1.5倍)、2h K线降低噪音

配置文件：output/configs/turtle_trading_i99.json
毕业报告：output/reports/turtle_trading_graduate.md

## [2026-05-22] ingest | Two Centuries Trend Following (CFM)

CFM波动率归一化EMA偏离时间序列动量。信号：s(t) = [price - EMA_p] / σ，n=3~7个月最优。研究方向：月频EMA偏离趋势、多周期信号组合、ATR止损版本。

## [2026-05-22] close | Two Centuries Trend Following — Discard (预验证失败)

结论：Discard。CFM波动率归一化EMA偏离信号在中国商品期货上无显著预测能力。
日频方向准确率49~51%，月频最高56.5%（仅j99 3mo）。
关键教训：与TSMOM一致，月频时间序列动量在中国商品期货上不显著。
教训记录到 wiki/lessons/cfm-trend-signal-chinese-commodity.md。

## [2026-05-22] ingest | Keltner Channel Breakout (PyQuantLab)

Keltner通道突破策略：EMA中轨+ATR通道+突破上下轨入场，回归EMA离场。已在BTC上验证Sharpe=1.11。研究方向：基础版、多周期版、ADX过滤版、波动率目标版。

## [2026-05-22] ingest | Concretum Intraday ATR Breakout

日内ATR通道突破策略（Concretum Group QuanTips #2）。基线策略：开盘价±0.5×ATR(14)日内通道突破入场，回归开盘价离场。研究方向：ATR通道日内突破、方向过滤版、波动率目标仓位版。

## [2026-05-22] close | Concretum Intraday ATR — Retain

结论：Retain。日内ATR通道策略在rb99上slippage=0 Sharpe=0.68，但含滑点后完全崩溃（-0.57）。
仅rb99有效，DCE合约（j99/i99/jm99）上爆仓或负收益。

## [2026-05-22] backtest | KeltnerBreakout on 4合约 → Retain

Keltner通道突破策略（1h K线，突破Keltner上下轨入场，回归EMA中轨离场）。

4品种全回测（slippage=0/1）+ 参数优化（520组合）+ 分段测试。

最终结果（默认参数，滑点=1）：
| 品种 | Sharpe | 总收益 | MaxDD | 交易次数 |
|------|:-----:|:-----:|:-----:|:-------:|
| rb99.SHFE | 0.51 | +11.1% | -4.8% | 388 |
| j99.DCE | 0.50 | +88.9% | -27.1% | 397 |
| i99.DCE | 0.45 | +26.8% | -13.7% | 389 |
| **jm99.DCE** | **0.61** | +66.2% | -16.9% | 393 |

分段测试（i99最优参数，零滑点）：前半Sharp=1.06 → 后半0.39，效应衰减严重。
决策：Retain。代码保留。

## [2026-05-22] graduate | ConcretumDualChannelV2b on jm99.DCE 🎓

第二个毕业策略！Donchian+EMA斜率过滤策略，2h K线适配版。

**最终参数（2h K线）：** entry_window=10, exit_window=8, ema_window=60, atr_stop_multiplier=4.0
**jm99.DCE 结果：** Sharpe=1.00, 总收益+60.6%, MaxDD=-11.4%
**rb99.SHFE 结果：** Sharpe=1.31 🏆, 收益+13.3%, MaxDD=-1.5%

优化路径：原版1h→2h K线 + 短通道(entry=10) + EMA60方向过滤 + 4倍ATR宽止损

配置文件：output/configs/concretum_dual_channel_graduate.json
毕业报告：output/reports/concretum_dual_channel_graduate.md

## [2026-05-31] close | Turtle Trading 研究项目 — Retain

经典海龟交易系统在4品种全正收益（i99 Sharpe=0.84最佳），策略含1h K线合成+Donchian突破+ATR止损。未达毕业标准但普适性好，代码保留。

## [2026-05-22] skip | 定时巡检 — 无新文章

定时投研流水线检查：无活跃进程。搜索了20+ Substack/Medium文章，未找到新的、非付费墙的、可直接编码的单品种CTA趋势跟踪策略文章。现有的公开文章大多已被处理或与已有内容重复。跳过本次执行。

## [2026-05-31] discard | Alpha Flow 波动率包络策略 — 5变体全负

双EMA基线 + ATR包络 + 体制锁定在BTCUSDT(2019-2026)上无alpha。最优Sharpe=0.07，所有变体Sharpe<0.1。ATR包络在加密高波下无法区分趋势/噪音，体制锁定+ATR止损导致回撤致命。教训记录到 wiki/lessons/alpha-flow-envelope-crypto.md。

## [2026-05-31] close | Alpha Flow 波动率包络研究 — Discard

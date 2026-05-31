# Wiki 内容目录

## 文章摘要（sources/）

- [Coding Trend Factor](sources/coding-trend-factor.md) — 多周期MA加权组合趋势因子，适配为CTA策略
- [Concretum Dual Channel](sources/concretum-dual-channel.md) — 双通道（Donchian+Keltner）趋势过滤，双重确认入场
- [Royal Purple Trend State Machine](sources/royal-purple-trend-state.md) — 三层EMA趋势状态机
- [Larry Williams Smash Day](sources/larry-williams-smash-day.md) — 反趋势反转模式
- [Improved TSMOM on Commodities Futures](sources/improved-tsmom-commodities-futures.md)
- [Concretum Intraday ATR Breakout](sources/concretum-intraday-atr-breakout.md) — 日内ATR通道突破
- [Two Centuries Trend Following](sources/two-centuries-trend-following.md) — 百年行业趋势跟踪
- [Intraday Momentum](sources/intraday-momentum.md) — 日内动量效应
- [RSI-2 Mean Reversion](sources/rsi-2-mean-reversion.md) — 趋势过滤的RSI-2均值回归
- [Turtle Trading (Rogue Quant)](sources/turtle-trading-rogue-quant.md) — 海龟交易系统在40+期货市场验证
- [Trade Like Mulvaney](sources/trade-like-mulvaney.md) — 逆向工程Mulvaney 26年长线趋势跟踪系统
- [Trend Following Replication](sources/trend-following-replication.md) — 多窗口动量z-score + 两层波动率归一化（skip: 信号不显著）
- [Regime-Dependent Trend Following](sources/regime-dependent-trend-following.md) — 体制检测+动态仓位，Sharpe TSM 0.21→OPT 0.51
- [Alpha Flow Volatility Envelope](sources/alpha-flow-volatility-envelope.md) — 波动率自适应双EMA趋势跟踪，体制锁定状态机
- [Gold Trend Following (Unger)](sources/unger-gold-trend-following.md) — CCI ±300极端值 + 日高低突破双策略

## 交易概念（concepts/）

- [ArrayManager API参考](concepts/array-manager-api.md) — 所有技术指标方法及参数签名
- [BarGenerator 使用指南](concepts/bar-generator-usage.md) — 多周期K线合成模式
- [CtaTemplate API参考](concepts/cta-template-api.md) — 策略基类的交易方法和生命周期
- [开仓入场逻辑 + 趋势过滤](concepts/entry-patterns.md) — 均线交叉、通道突破、指标阈值、方向过滤
- [平仓离场逻辑 + 移动止损](concepts/exit-patterns.md) — 反向信号、时间平仓、ATR/百分比/布林带止损
- [仓位管理](concepts/position-sizing.md) — 固定手数、ATR风险调整、金字塔加仓
- [策略代码规范](concepts/code-conventions.md) — 命名风格、helper函数、类型提示、docstring

## 策略设计（strategies/）

| 策略 | 状态 | 核心逻辑 | 最优Sharpe |
|------|------|---------|:----------:|
| [TurtleTrading](strategies/turtle-trading.md) | 🎓 **已毕业** | Donchian突破+EMA过滤+ATR止损(2h) | **1.03** |
| [MultiMaTrend](strategies/multi-ma-trend.md) | 已产出 | 多周期MA趋势因子，阈值穿越 | 0.58 |
| [IntradayMomentum](strategies/intraday-momentum.md) | 已产出 | 开盘区间突破，日内交易 | 0.74 |
|| [ConcretumDualChannel](strategies/concretum-dual-channel.md) | 🎓 **已毕业** | Donchian+EMA双通道+4倍ATR止损(2h) | **1.31** |
| [TrendStateMachine](strategies/trend-state-machine.md) | 已产出 | 三层EMA趋势状态机 | 0.78 |
| [SmashDay](strategies/smash-day.md) | 已产出 | Larry Williams反转模式 | 0.49 |
| [ConcretumIntradayATR](strategies/concretum-intraday-atr.md) | 已产出 | 日内ATR通道突破 | 0.68 |
| [KeltnerBreakout](strategies/keltner-breakout.md) | 已产出 | Keltner通道突破，EMA中线离场 | 0.61 |
| [CciExtremeTrend](strategies/cci-extreme-trend.md) | 已产出 | CCI ±300极端值趋势跟踪，ATR止损 | 0.61 |

## 经验教训（lessons/）

- [高频趋势跟踪的滑点陷阱](lessons/slippage-trap.md) — 零滑点回测的Sharpe不可信，必须加入真实成本验证
- [1小时通道突破必须用停止单](lessons/stop-order-breakout.md) — 收盘价判断会错过盘中突破
- [TSMOM在中国商品期货上不成立](lessons/tsmom-chinese-commodity.md) — 日频t-stat TSMOM准确率≤52%
- [日内ATR通道突破的滑点陷阱](lessons/atr-channel-intraday-slippage.md) — 高频策略的滑点敏感性分析
- [三层EMA状态机的信号延迟](lessons/ema-layer-spacing.md) — EMA层间距与信号延迟的关系
- [反转策略的品种特异性](lessons/reversal-cross-market-specificity.md) — 美国有效不等于中国有效
|- [ATR止损与反突破离场重叠](lessons/turtle-redundant-exit-logic.md) — 两套离场机制同时存在导致参数无效
|- [加密实盘费率实测：22个策略10天26,765笔交易](lessons/crypto-fee-drag-22-strategies.md) — 趋势跟踪全灭，RSI均值回归全赢，费率是杀手

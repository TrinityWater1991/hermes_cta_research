# Concretum Dual Channel 策略研究

## 状态：关闭（Retain）

## 来源

- Concretum Group: "A Century of Profitable Industry Trends" (SSRN 4857230)
- 从双通道思想适配为单品种 CTA

## 研究结论

**最优版本**: v2b（Donchian + EMA 斜率过滤，停止单版）

在4个品种上测试结果：
- **jm99.DCE**: Sharpe=0.96, Ret=56.5%, DD=-6.8%（✅ 接近毕业，两段均>1.0）
- **i99.DCE**: Sharpe=0.76, Ret=18.9%, DD=-7.8%
- **rb99.SHFE**: Sharpe=0.74, Ret=7.0%, DD=-1.7%
- **j99.DCE**: Sharpe=0.38, Ret=35.6%, DD=-19.1%（较弱）

**关键经验**：
1. 停止单方式是1小时K线策略正确入场方式
2. 方向过滤比双重通道确认更有效
3. jm99（焦煤）是该策略的最佳品种

## 最优参数

- entry_window: 40
- exit_window: 20
- ema_window: 20
- atr_stop_multiplier: 3.0

## 策略代码

`strategies/concretum_dual_channel_v2b_strategy.py` — 保留
`strategies/concretum_dual_channel_v1b_strategy.py` — 保留（参考）
`strategies/concretum_dual_channel_v3b_strategy.py` — 保留（参考）

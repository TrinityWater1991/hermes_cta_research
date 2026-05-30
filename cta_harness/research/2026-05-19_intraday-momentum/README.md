# 研究项目：Intraday Momentum

## 状态：关闭（Retain）

## 来源

- Quantitativo: "Intraday Momentum for ES and NQ"
- 学术支撑："Intraday Time-series Momentum: Evidence from China"

## 研究结论

日内动量的纯方向信号在rb99上无效，但Opening Range Breakout（开盘区间突破）模式有效。最优策略在slippage=0下Sharpe=0.74，两段分期测试均为正收益，但未达毕业标准（Sharpe<1.0）。效应在2021年后明显衰减。

## 最优参数

- observation_minutes: 55
- range_multiplier: 1.0
- atr_stop_multiplier: 6.5
- exit_time: 14:45

## 策略代码

`strategies/intraday_momentum_strategy.py` — 保留

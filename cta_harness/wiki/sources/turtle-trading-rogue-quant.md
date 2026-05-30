# Turtle Trading Strategy 在40+期货市场上的回测验证

## 来源
- **标题**: I Backtested The Legendary Turtle Trading Strategy Across 40 Futures Markets
- **作者**: The Rogue Quant
- **日期**: 2025-08-15
- **链接**: https://roguequant.substack.com/p/i-backtested-the-legendary-turtle

## 摘要
作者使用原始 Turtle 交易系统的规则（1983年版），在43个不同的期货市场上进行了18年（2007-2025）的回测。**没有任何参数优化或曲线拟合**。总利润 $1,147,318，但不同市场间差异极大——有强趋势的市场表现优异，震荡市则表现糟糕。

## 关键思路
Turtle 系统是一套经典的 CTA 趋势跟踪策略，核心逻辑：
1. **入场**: 价格突破过去20日最高点时做多，突破20日最低点时做空
2. **离场**: 价格反向突破过去10日最高点/最低点时平仓
3. **仓位管理**: 基于 ATR 的波动率调整仓位大小
4. **止损**: ATR 倍数止损

## 策略方向
### 方向1: 经典 Turtle 系统（20日突破入场 + 10日反突破离场）
- Donchian Channel(20) 突破入场
- Donchian Channel(10) 反向突破离场
- ATR 波动率调整仓位
- ATR 倍数止损（如 2ATR 止损）
- 多空双向

### 方向2: Turtle 系统 + EMA 趋势过滤
- 在经典 Turtle 基础上增加 EMA 方向过滤
- 仅在大趋势方向上开仓（减少假突破）
- 类似 Concretum v2b 的过滤思路

### 方向3: Turtle 系统 + ATR 动态止损改进
- 将 10日反向突破离场改为 ATR trailing stop
- 更灵活地捕捉趋势延续
- 可减少早出场问题

## 品种适配
- 螺纹钢 rb99.SHFE（趋势性品种）
- 焦炭 j99.DCE（高波动）
- 铁矿 i99.DCE
- 焦煤 jm99.DCE（已验证可在0.5-1.0+ Sharpe范围）

## 预期K线周期
- 主周期: 1小时（BarGenerator 合成）
- 日线也可考虑（经典 Turtle 本身是日线策略）

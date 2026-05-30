# Concretum Intraday ATR Breakout Strategy

**来源：** [Improving Performance with Fast Alphas: A Tactical Overlay for Intraday Trend Trading](https://concretumgroup.com/wp-content/uploads/2026/02/Improving-Performance-with-Fast-Alphas-A-Tactical-Overlay-for-Intraday-Trend-Trading.pdf)
— Concretum Group, QuanTips #2, February 2026

**作者：** Carlo Zarattini, Alberto Pagani

**日期：** 2026-05-22

---

## 策略框架

### 基线日内趋势策略（可货币化Alpha）

**入场规则：**
- 计算 ATR(14) 基于日内K线
- 上轨 = 当日开盘价 + 0.5 × ATR(14)
- 下轨 = 当日开盘价 - 0.5 × ATR(14)
- **多头入场：** 价格收于上轨之上
- **空头入场：** 价格收于下轨之下

**离场规则：**
- **止损：** 价格回到开盘价（方向回归均值）
- **强制平仓：** 收盘前全部平仓

**执行频率：** 每15分钟检查一次（整点:00/:15/:30/:45）

**仓位管理：** 波动率目标（14日回溯期，每日波动率目标2%）

### 增强版（快速Alpha执行覆盖）

- 入场条件化：突破信号出现后，等待5分钟级别的反向运动再执行
- 离场条件化：止损触发时，等待5分钟级别的短期回摆再平仓

---

## 基线策略表现

| 指标 | 值（净成本后） |
|------|--------------|
| CAGR | >13% |
| Sharpe | ~0.87 |
| 标的 | SPY ETF |
| 数据 | 2007-01 ~ 2026-01, 5min bars |
| 交易成本 | IBKR tiered佣金 + 监管费 |

---

## 可实现的策略方向

### 方向1：日内ATR通道突破（基线版）✅（主要方向）
- 日内1小时K线，开盘价±ATR(14)通道
- 价格突破通道入场，回到开盘价离场
- 日内平仓

### 方向2：日内ATR通道 + 方向过滤
- 添加EMA趋势方向过滤
- 仅在主趋势方向做突破

### 方向3：日内ATR通道 + 波动率目标仓位
- ATR波动率估计调整仓位
- 低波动率时放大仓位，高波动率时缩减

---

## 与已有策略的差异对比

| 维度 | 本策略 | Opening Range Breakout | Donchian Channel |
|------|-------|----------------------|-----------------|
| 通道定义 | ATR(14) × 0.5 | 开盘30分钟高低点 | N日最高最低 |
| 入场时机 | 日内持续监测 | 开盘30分钟后 | 任意时点 |
| 离场逻辑 | 回归开盘价（均值回归） | 尾盘固定离场 | 反向通道突破 |
| 持仓周期 | 日内 | 日内 | 数日~数周 |

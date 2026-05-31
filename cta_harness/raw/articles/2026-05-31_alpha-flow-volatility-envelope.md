# The Bitcoin Strategy That Beats Buy & Hold — Alpha Flow Strategy

**来源:** On-Chain Mind Newsletter (Nov 21, 2025)
**URL:** https://onchainmind.substack.com/p/the-bitcoin-strategy-that-beats-buy

---

## 核心概念

一个机械化的波动率自适应趋势跟踪系统，自2012年以来将$1,000变成$95.7M（134% CAGR），远超买入持有（104% CAGR）和定投（59% CAGR）。

核心哲学：**反应，不预测**。系统只回答两个问题：
1. 当前是否存在真正的趋势？
2. 趋势是否已被明确打破？

## Alpha Flow 策略三组件

### 1. 双EMA基线 (Dual-EMA Baseline)
- 混合快速和慢速EMA的典型价格(HLC/3)
- 比单一MA更灵敏，比裸价格更平滑

### 2. 波动率包络 (Volatility Envelopes)
- 对基线计算平滑标准差，乘以倍数形成上下轨
- 与固定百分比的Bollinger Bands不同，偏差适应实际趋势波动率

### 3. 体制锁定状态机 (Regime-Locking State Machine)
- **Bull信号触发**: 价格收盘在上轨之上
- **Bear信号触发**: 价格收盘在下轨之下  
- **体制锁定直到反向信号**: 避免正常回调中的反复穿越(whipsaw)

> "Bitcoin has to prove beyond reasonable doubt that the trend is dead before the system lets you get hurt."

## 策略方向

1. **Alpha Flow基础版**: 双EMA基线 + 波动率包络 + 体制锁定状态机
2. **EMA方向过滤版**: 增加长期EMA过滤确保只在主趋势方向交易
3. **多时间框架版**: 日线确定体制，小时线执行入场
4. **自适应参数版**: 波动率倍数随市场体制自动调整

## 关键特点
- 基于收盘价决策（非盘中穿越），减少噪音
- 体制锁定机制防止频繁翻转
- 波动率自适应（非固定百分比），适合加密市场高波动特性

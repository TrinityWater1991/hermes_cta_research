# Gold Trend Following (Unger Academy)

**来源:** [Unger Academy](https://ungeracademy.com/blog/trend-following-strategies-gold-future-2025)
**作者:** Andrea Unger
**日期:** 2025
**合约:** COMEX Gold futures

---

## 文章摘要

Andrea Unger 分析了两个在 2025 年黄金强势行情中表现优异的趋势跟踪策略：

### 策略1: CCI 极端值趋势跟踪
- 反直觉使用 CCI：±300（而非标准 ±100）作为趋势确认
- 入场：CCI 上穿 +300（做多）/ 下穿 -300（做空）
- 离场：CCI 回归零附近
- 信号稀有但爆发性强，几百笔交易，均利 >$200

### 策略2: 前日高低突破
- 纯价格行为：前一时段高/低点作为突破水平
- 入场：止损单置于前日高点之上/低点之下
- 离场：固定金额止损 + 固定金额止盈
- ~1,300笔交易，均利 ~$370，盈亏比 >2:1，胜率 <40%

## 适配方向

1. **CCI 极端值版**: CCI(period) ±300 阈值，入场/出场逻辑移植到加密/期货单标的
2. **日高低突破版**: 用 BarGenerator 合成日 K线，适配 24×7 加密无收盘特性
3. **混合版**: CCI 确认方向 + 固定 ATR 倍数止损止盈

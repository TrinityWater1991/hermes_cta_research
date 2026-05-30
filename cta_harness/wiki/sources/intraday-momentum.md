# Intraday Momentum for ES and NQ

## 来源

- 文章：Quantitativo, "Intraday Momentum for ES and NQ"
- URL：https://www.quantitativo.com/p/intraday-momentum-for-es-and-nq
- 相关学术论文：
  - Gao et al. "Market Intraday Momentum" (2018) — S&P 500 ETF前半小时收益预测尾盘收益
  - "Intraday Time-series Momentum: Evidence from China" — 中国商品期货（铜、钢材、大豆、豆粕）验证同一效应
  - Zarattini et al. "Beat the Market: An Effective Intraday Momentum Strategy" (2024) — 异常动量出现时立即入场

## 核心思路

日内动量效应：交易日前半小时的收益方向能正向预测尾盘（最后半小时）的收益方向。

机制解释：
- 开盘阶段反映隔夜信息的消化
- 信息在日内逐步扩散，形成持续性动量
- 尾盘机构调仓放大了方向性运动

## 策略方向

1. **Opening Range Momentum**：开盘后30-60分钟观察收益方向和幅度，超过阈值时顺方向入场，收盘前平仓
2. **隔夜跳空延续**：开盘跳空超过阈值时顺方向入场，利用日内动量延续
3. **多时段动量确认**：结合前半小时和午盘方向，双重确认后入场

## 适配中国期货的考虑

- SHFE交易时段：21:00-23:00（夜盘）+ 09:00-10:15 + 10:30-11:30 + 13:30-15:00
- 夜盘开盘（21:00）是主要信息释放窗口
- 日盘开盘（09:00）是第二个信息窗口
- 需要处理跨时段的时间逻辑
- 学术研究确认钢材期货存在此效应

## 风险提示

- Yang et al. 警告：日内策略可能无法覆盖交易成本
- 需要阈值过滤，只在强动量日交易
- 每笔利润必须远大于滑点成本（rb99需>50元/笔）

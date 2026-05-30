# RSI-2 Mean Reversion with Trend Filter (Connors-Style)

**来源**: [Engineering Alpha / Sofien Kaabar, CFA](https://abouttrading.substack.com/p/back-testing-a-famous-profitable)
**日期**: 2021-10-30
**状态**: 活跃研究中

## 摘要

Larry Connors 著名的 RSI-2 均值回归策略：使用 2 周期 RSI 的超买超卖信号，配合 200 周期 SMA 作为趋势过滤器。当价格在 200-SMA 之上且 2-period RSI 低于 5 时做多，当价格在 200-SMA 之下且 2-period RSI 高于 95 时做空。

## 核心策略逻辑

- **做多条件**: 价格 > 200-SMA 且 2-period RSI < 5（超卖+上升趋势）
- **做空条件**: 价格 < 200-SMA 且 2-period RSI > 95（超买+下降趋势）
- **出场规则**: 价格突破 5 周期 MA
- **原文测试**: EURUSD 小时线，命中率 78%，盈亏比 0.47

## 潜在研究方向

1. **RSI-2 均值回归（期货版）**: 在商品期货日线/1h 上测试 RSI-2 入场 + 200-MA 趋势过滤器
2. **参数自适应**: 优化 RSI 阈值和 MA 周期（如 100/50-MA 替代 200）
3. **多周期确认**: 结合更大周期的趋势确认，减少假信号
4. **RSI 背离**: 在 RSI-2 基础上加入价格与 RSI 的背离信号
5. **反向策略**: 在趋势强时使用 RSI 不超买/超卖信号作为趋势延续入场

## 适用品种

适用于所有有趋势特征的商品期货品种。由于 RSI-2 是极端价格行为信号，更适合趋势性强的品种（焦煤、铁矿石、焦炭），振幅较大的品种也能提供更多极端值机会。

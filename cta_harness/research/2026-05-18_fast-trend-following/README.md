# Fast Trend Following 研究项目

## 来源

文章：[Fast trend following](../raw/articles/2024-12-11_fast-trend-following.md) by Quantitativo

## 核心思路

使用双Kalman滤波器（快/慢）的偏离百分位数作为趋势强度指标，超过阈值入场，回归离场。

## 研究方向

1. **Kalman趋势指标策略** — 忠实还原文章思路，15分钟线
2. **双EMA偏离策略** — 用EMA简化Kalman，1小时线
3. **KAMA自适应趋势策略** — 利用KAMA+ATR通道，15分钟线

## 回测参数

- 合约：rb99.SHFE
- 数据：2016-05-06 ~ 2026-05-08
- rate=0.0001, size=10, pricetick=1, slippage=0, capital=200,000

## 状态

已关闭（Discard）— 策略无法承受真实交易成本

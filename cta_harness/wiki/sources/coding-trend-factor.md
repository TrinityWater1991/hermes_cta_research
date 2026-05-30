# Coding Trend Factor

## 来源

- 文章：[Coding Trend Factor](https://www.quantitativo.com/p/coding-trend-factor) by Quantitativo (2025-02-07)
- 论文：Han, Zhou, Zhu (2016) "A Trend Factor: Any Economic Gains from Using Information Over Investment Horizons?" Journal of Financial Economics

## 摘要

文章实现了一个"趋势因子"：用多周期移动平均线（3/5/10/20/50/100/200/400/600/800/1000日）的归一化信号加权组合，预测资产收益方向。原文应用于股票横截面排序，但核心思路可适配为单标的CTA策略。

## 核心思路

1. 计算多个周期的MA，归一化为 MA/Price - 1（消除价格量纲）
2. 用历史回归系数的滚动均值作为各MA信号的权重
3. 加权求和得到"趋势因子"分数
4. 分数高→做多，分数低→做空

## 适配为CTA策略的方向

1. **多周期MA加权趋势指标**：用固定权重（或等权）组合多周期MA信号，作为趋势强度指标。信号为正做多，为负做空。
2. **简化版：短中长三周期MA投票**：选3个代表性周期（如20/60/200），多数看多则做多。
3. **自适应权重版**：用滚动窗口内各MA信号与未来收益的相关性作为动态权重。

# Rethinking Trend Following: Optimal Regime-Dependent Allocation

**来源**: Quantocracy → Alpha Architect / SSRN (ID 6376479)  
**原文**: https://alphaarchitect.com/rethinking-trend-following-optimal-regime-dependent-allocation/  
**论文**: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6376479  
**入库日期**: 2026-05-31  
**状态**: 待验证

## 摘要

传统趋势跟踪研究聚焦信号构建（怎么更好地检测趋势）。本文反过来问：**已知市场体制后，最优仓位是多少？** 作者从第一性原理推导出每个体制的 Sharpe 最优组合权重，创建了一个简单可操作的框架。

核心发现：标准趋势跟踪规则（如 +1/-1 全仓多空）只是该框架的特例，且通常**次优**。

## 核心策略思路

### 两体制（牛/熊）
- 基准：Moskowitz et al. (2012) TSM，平均 OOS Sharpe **0.208**
- 最优：**Sharpe 0.506**（平均提升 +0.299）

### 四体制（牛/熊/修正/反弹）
- 基准：Goulding et al. (2023) DSM，平均 OOS Sharpe **0.496**
- 最优：**Sharpe 0.628**（平均提升 +0.132）

### 惊人发现
**熊市最优暴露通常接近零，甚至轻微做多**——直接挑战了趋势跟踪中"跌就满仓空"的常识。

### 框架要点
- 不需要发明新信号，只需要**更聪明地分配已知体制的仓位**
- 估计体制特定的预期收益和风险 → 直接计算最优暴露
- 适用于战术资产配置、管理期货/CTA 策略

## 潜在策略方向

1. **体制检测 + 动态仓位**：用 ATR/波动率分位数定义体制（高波=熊，低波=牛），不同体制用不同仓位倍数
2. **信号 × 体制矩阵**：原有趋势信号（如 MA 穿越）仅判断方向，体制判断决定仓位大小（0.5x/1x/2x）
3. **简化版**：趋势信号做多时，若波动率>阈值则仓位减半（熊市不重仓）

## 结论

_待验证_

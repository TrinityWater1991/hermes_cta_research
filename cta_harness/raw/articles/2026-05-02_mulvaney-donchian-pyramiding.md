# You Can Trade (Almost) Like Mulvaney – Reverse Engineering a Trading Legend

**来源:** Concretum Group (Substack)
**日期:** 2026-05-02
**作者:** Concretum Research
**URL:** https://concretumgroup.substack.com/p/you-can-trade-almost-like-mulvaney

## 摘要

Paul Mulvaney，Mulvaney Capital Management CEO，自1999年起运行全系统化CTA趋势跟踪策略，26年年化约20%，$100K投入可增长至近$1000万（净费用后）。2022-2026年表现尤为亮眼（+89%, +51%, +83%, +65% YTD Mar 2026）。

文章通过4320个合成CTA程序网格扫描，对Mulvaney的策略进行了反向工程。

## 五大已知特性

1. **广泛期货组合**：45个期货市场（股票、利率、外汇、能源、金属、软商品、农产品、牲畜）
2. **Donchian通道突破**：N日新高做多，N日新低做空，长期持仓（~6个月）
3. **金字塔加仓**：趋势发展中逐步加仓，盈利达到预定阈值触发加仓
4. **波动率追踪止损，无止盈**：仅止损离场，无获利了结。初始固定止损→满仓后每日波动率追踪止损（Donchian中线代理）
5. **风险基础仓位管理**：等亏损平价 / 分层亏损平价

## 核心伪代码

```
入场: Long if Close >= Donchian High; Short if Close <= Donchian Low
初始固定止损: Channel Width = Donchian High - Donchian Low
  多: Donchian High - p × Channel Width
  空: Donchian Low + p × Channel Width
追踪止损: Donchian Midline = (High + Low) / 2
仓位: Contracts = (15% × Equity / N_Markets) / DollarStopRisk
金字塔乘数: r = 持仓盈利/初始止损风险, m = min(cap, 1 + floor(max(0, r)/K))
现金: 期货P&L + 无风险利率-100bps抵押收益
```

## 反向工程关键发现

- **长期入场窗口最佳**：Donchian lookback 在120-250天区间（对应~6个月持仓）
- **固定止损 p≈0.5 普遍较好**
- **等亏损平价 vs 分层平价**：结果相似
- **仅做多变体**在某些时期表现优于双向

## 潜在策略方向

1. **Donchian中线追踪止损单标的版**：将Donchian中线追踪止损机制适配加密单标的，1h/4h K线
2. **金字塔加仓单标版**：BTC单标的上实现基于盈利阈值的金字塔加仓，r=margin_profit/initial_stop_risk
3. **简化Mulvaney系统**：仅做多+Donchian通道突破(120-250天窗口)+中线追踪止损+波动率仓位
4. **Mulvaney止损系统测试**：固定初始止损 vs 中线追踪止损 vs 两者组合在BTC上的对比

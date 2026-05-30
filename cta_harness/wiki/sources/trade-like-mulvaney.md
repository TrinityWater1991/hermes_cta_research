# You Can Trade (Almost) Like Mulvaney — Concretum Group

**来源**: [Concretum Group Substack](https://concretumgroup.substack.com/p/you-can-trade-almost-like-mulvaney)
**日期**: 2026-05 (推测)
**作者**: Concretum Research

---

## 核心思路

对 Paul Mulvaney（Mulvaney Capital Management）的 26 年长线趋势跟踪系统进行逆向工程。Mulvaney 的 CTA 自 1999 年运行至今未变：~20% 年化复利，$100K→$10M。

### 入场：Donchian 通道突破（126 交易日 ≈ 6 个月）
```
Long if Close >= Donchian High
Short if Close <= Donchian Low
```

### 初始止损
```
通道宽度 = Donchian High - Donchian Low
Long Stop = Donchian High - (通道宽度 / 3)
```

### 追踪止损
- Donchian Midline = (Donchian High + Donchian Low) / 2
- 单向移动（只向上/向下），不准回拉
- **无止盈目标**——只通过止损离场
- 关键原则：不止盈才能捕获无限上行潜力

### 仓位管理
- 跨 45 个期货市场等风险分配
- 金字塔加仓：随浮盈增加逐步加仓

### 执行
- 信号后 24-48 小时窗口内入场
- 无方向偏好，对称处理多空

### 关键参数
- Donchian Lookback: 126 天（~6 个月）
- 初始止损偏移: 1/3 通道宽度
- 仓位: 等风险分配（15% 总风险预算）

---

## 策略研究方向

1. **Mulvaney Mimic（日频）** — 126日Donchian通道突破，ATR止损，中线追踪止。日频K线，适合商品期货长期趋势跟踪
2. **短通道变体（周频）** — 不同Donchian周期（63/126/252日）对比
3. **中线追踪止损** — Donchian中线的追踪特性分析

---

## 与中国商品期货的相关性

- 日频/周频长期趋势跟踪，交易频率低（年均~10-20次），滑点成本阻力小
- 4种商品（rb99/j99/i99/jm99）均有明显的长期趋势特征
- 适合中国商品期货的长期 CTA 策略

## 关键教训
- Mulvaney 的真正优势：25 年不修改策略的心理纪律
- 82% 的月份处于浮亏状态，需要极端心理承受力
- 简单的规则 + 极致的纪律 = 长期超常回报

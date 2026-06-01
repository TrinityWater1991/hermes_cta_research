# Donchian 通道计算陷阱：包含当前 bar 导致零交易

**发现日期**: 2026-06-01
**影响**: MulvaneyTrendStrategy

## 问题

Donchian 通道突破的标准入场条件是：`Close >= Donchian High (过去N期最高价)`。

但如果 Donchian High 的计算包含了当前 bar（`am.high[-n:]`），则：
- Donchian High = max(high[-n:])，包含当前 bar 的 high
- 当前 bar 的 close ≤ 当前 bar 的 high
- ∴ close 永远不可能 ≥ Donchian High（除非 close == high 且是 N 期最高）

这导致入场条件极其苛刻，在 200 期 Donchian 上几乎从不触发。

## 解决方案

计算 Donchian 时排除当前 bar（索引 -1）：

```python
# ❌ 包含当前 bar
self.donchian_high = float(max(am.high[-n:]))

# ✅ 排除当前 bar（索引 -1）
self.donchian_high = float(max(am.high[-(n + 1):-1]))
```

这样 Donchian High 基于过去 N 根 bar，入场条件变为：当前 close 突破过去 N 根 bar 的最高价。

## 教训

任何基于"价格突破历史极值"的策略，必须确保历史极值的计算窗口不包含当前 bar。这适用于：
- Donchian 通道
- Keltner 通道（如使用 historical max/min）
- 布林带（虽然标准差包含当前 bar 影响较小）
- 任何 "N 期最高/最低" 指标

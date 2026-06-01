# 迭代记录

## v1 — 2026-06-01 — 初始版本

**方向**: Donchian 集成（精简版：5/20/60/150/360 五个 lookback）
**特点**: 
- 日线 BarGenerator (Interval.DAILY, daily_end=time(0,0))
- Donchian Channel on close prices (排除当前 bar)
- DonchianMid 单向追踪止损（只上移不下移，用最长 lookback 360）
- Ensemble: 5 个模型等权投票，信号 ≥ 0.5 入场
- 动态仓位（capital/ATR × multiplier）
- ruff ✅, mypy ✅ (仅预存 import-untyped)

**待完成**: 回测验证

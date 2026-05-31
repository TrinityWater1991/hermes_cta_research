# MultiZScoreTrend 策略设计

**来源**: Trend Following Replication (Beyond Passive)  
**状态**: 已淘汰（discard）

## 核心逻辑

- 4个动量窗口 [40, 80, 160, 320] 在 1h K线上计算 z-score
- z-score = 窗口对数收益 / (波动率 * sqrt(窗口))
- 等权平均 → 综合趋势信号
- z-score 穿越 0 入场，回归 0 离场
- ATR 移动止损

## 参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| zscore_window1-4 | 40/80/160/320 | 动量窗口 |
| vol_window | 63 | 波动率窗口 |
| entry_threshold | 0.0 | 入场阈值 |
| atr_window | 20 | ATR周期 |
| atr_stop_multiplier | 3.0 | ATR止损倍数 |

## 回测结果

_待更新_

# vnpy BarGenerator 窗口限制

**发现日期**: 2026-06-01
**影响**: MulvaneyTrendStrategy（及其他需要非标准分钟K线的策略）

## 问题

vnpy 的 `BarGenerator` 在合成 x 分钟 K线时有严格限制：

```python
# vnpy/trader/utility.py L172-173
# 1. for x minute bar, x must be able to divide 60: 2, 3, 5, 6, 10, 15, 20, 30
# 2. for x hour bar, x can be any number
```

使用 `interval=Interval.MINUTE`（默认）时，window 必须是 60 的约数：2, 3, 5, 6, 10, 15, 20, 30, 60。

## 症状

- window=120/90/80/70/65 等非整除 60 的值 → `on_window_bar` 从不触发 → 0笔交易
- 无任何报错或警告

## 解决方案

能整除 60 的窗口用 `Interval.HOUR`：

```python
if self.bar_interval_minutes % 60 == 0:
    hours = self.bar_interval_minutes // 60
    self.bg = BarGenerator(
        self.on_bar, hours, self.on_window_bar, Interval.HOUR,
    )
else:
    # 仅支持 2,3,5,6,10,15,20,30,60
    self.bg = BarGenerator(
        self.on_bar, self.bar_interval_minutes, self.on_window_bar,
        Interval.MINUTE,
    )
```

| bar_interval_minutes | Interval | window | 说明 |
|---------------------|----------|--------|------|
| 60 | HOUR | 1 | 1h |
| 120 | HOUR | 2 | 2h |
| 240 | HOUR | 4 | 4h |
| 30 | MINUTE | 30 | 30min（整除60）|
| 15 | MINUTE | 15 | 15min |
| 90 | — | — | **不支持！** |

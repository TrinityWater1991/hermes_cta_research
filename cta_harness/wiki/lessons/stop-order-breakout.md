# 1小时通道突破策略必须使用停止单

## 问题

在1小时K线级别的通道突破策略（如 Donchian、双通道等）中，如果使用 `close > donchian_up` 的方式判断入场，交易次数极少甚至为0。

## 原因

1小时K线的收盘价很少落在通道边界之外——大部分突破发生在K线内部（盘中价格穿越通道），到收盘时价格已经回到通道内。因此收盘价判断会错过几乎所有有效交易信号。

## 解决方案

使用 `stop=True` 的停止单（Stop Order）来捕获盘中突破：

```python
# ❌ 收盘价判断（错过大部分交易）
if self.ema_slope_up and close > self.donchian_up:
    self.buy(close, self.fixed_size)

# ✅ 停止单（捕获盘中突破）
if self.ema_slope_up and self.donchian_up > bar.close_price:
    self.buy(self.donchian_up, self.fixed_size, stop=True)
```

## 注意

- 停止单的触发条件要求 `stop price > current price`（对 buy stop）
- vnpy 的 `cancel_all()` 会在每根K线开始时撤销未成交的停止单
- 所以需要在每根K线重新挂单
- 不要同时对上下两个方向挂停止单——会导致双向频繁触发（v1b 的教训）

# 仓位管理

## 1. 固定手数

最简单的方式，每次交易固定合约数量。

```python
# 参数
fixed_size: int = 1

# 使用
self.buy(price, self.fixed_size)
```

适用：初期回测验证策略逻辑时。
来源：double_ma_strategy.py, boll_channel_strategy.py

## 2. ATR反向风险调整

仓位与波动率成反比：波动大时减仓，波动小时加仓。核心思想是每笔交易承担相同的风险金额。

```python
# 参数
risk_level: int = 300  # 风险系数（越大仓位越大）

# 计算
self.atr_value = self.am.atr(self.atr_window)
self.trade_size = max(1, int(self.risk_level / self.atr_value))

# 使用
self.buy(price, self.trade_size, stop=True)
```

原理：`risk_level / atr_value` 使得每手承担的价格波动风险大致恒定。

适用：趋势跟踪策略，需要在不同波动率环境下保持一致的风险暴露。
来源：pulse_strategy.py, aegis_strategy.py

## 3. 海龟式金字塔加仓

初始建仓后，价格每移动0.5个ATR加仓一次，最多4个单位。

```python
# 参数
fixed_size: int = 1  # 每个单位的合约数

def send_buy_orders(self, price: float) -> None:
    t = self.pos / self.fixed_size  # 当前持仓单位数

    if t < 1:
        self.buy(price, self.fixed_size, True)
    if t < 2:
        self.buy(price + self.atr_value * 0.5, self.fixed_size, True)
    if t < 3:
        self.buy(price + self.atr_value, self.fixed_size, True)
    if t < 4:
        self.buy(price + self.atr_value * 1.5, self.fixed_size, True)
```

原理：趋势确认后逐步加仓，每次加仓间隔0.5 ATR，总风险可控。
来源：turtle_signal_strategy.py

## 4. 每日交易次数限制

限制日内交易频率，避免过度交易。

```python
# 参数
daily_limit: int = 5

# 新一天重置计数
if new_day:
    self.daily_count = 0

# 入场前检查
if self.daily_count < self.daily_limit:
    self.buy(price, self.fixed_size)
    self.daily_count += 1
```

来源：surge_strategy.py

## 选择建议

| 场景 | 推荐方式 |
|------|----------|
| 策略逻辑验证阶段 | 固定手数 |
| 单品种趋势跟踪 | ATR反向风险调整 |
| 强趋势追踪 | 金字塔加仓 |
| 日内高频策略 | 固定手数 + 次数限制 |

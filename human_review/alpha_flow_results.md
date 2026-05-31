# AlphaFlow v2 回测结果

## 策略参数
- vol_multiplier=3.0
- filter_ema_period=0
- use_dynamic_size=true
- position_multiplier=0.005
- fast_ema_period=20, slow_ema_period=50

## 全量回测 (BTCUSDT.BINANCE 1m, 2020-01-01 ~ 2026-05-30)

| 指标 | 值 |
|------|-----|
| Sharpe | 1.00 |
| 总收益 | +160.6% |
| 最大回撤 | -11.8% |
| 交易次数 | 520 |
| 资本 | 200,000 |

## 版本对比
| 版本 | Sharpe | 收益 | MaxDD |
|------|:------:|------|------:|
| 固定仓位 | 0.45 | +22.2% | -7.3% |
| 动态仓位 | 1.00 | +160.6% | -11.8% |

## 核心逻辑
- HLC/3均价 → 双EMA(20/50) → baseline
- 通道: baseline ± 3.0×ATR
- 入场: 收盘价突破upper(体制翻转为1)
- 离场: 收盘价<lower / ATR trailing stop
- 仓位: capital/ATR × 0.005 (ATR高缩仓、低加仓)

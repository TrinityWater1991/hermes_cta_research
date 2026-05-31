# Alpha Flow 波动率包络策略研究

**来源:** [wiki/sources/alpha-flow-volatility-envelope.md](../../wiki/sources/alpha-flow-volatility-envelope.md)
**日期:** 2026-05-31
**状态:** 🔬 开发中

## 研究方向

1. **Alpha Flow 基础版 (v1)**: 双EMA基线 + 波动率包络 + 收盘价体制锁定
   - 基线 = (fast_EMA(HLC/3) + slow_EMA(HLC/3)) / 2
   - 上轨 = 基线 + k × std(基线)
   - 下轨 = 基线 - k × std(基线)
   - Bull: close > 上轨 → 做多；Bear: close < 下轨 → 平多
   - 体制锁定：Bull状态不因回调翻转，除非close < 下轨

2. **EMA方向过滤版 (v2)**: 增加长期EMA(如60周期)确保只在主趋势方向交易

3. **做多做空双向版 (v3)**: Bear信号也做空

## 回测参数

- 合约: BTCUSDT.BINANCE（优先）/ BNBUSDT.BINANCE
- 数据周期: 1m（BarGenerator合成1h K线）
- 回测区间: 数据可用最长区间
- capital: 200,000
- size: 1
- rate: 0.0004
- pricetick: 0.01
- slippage: 0 → 1

## 关键假设

- 收盘价体制锁定比盘中判断更稳健（加密假突破多）
- 基线波动率包络比价格ATR通道更适合趋势检测
- 双EMA比单EMA提供更平滑的趋势参考

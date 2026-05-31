# 迭代记录

## v1 (2026-05-31) — BTCUSDT 默认参数
- windows [40,80,160,320], entry_threshold=0, atr_stop=3.0
- Sharpe -0.44, 收益 -21%, MaxDD -28%, 2584笔
- ❌ 失败

## v2 (2026-05-31) — BTCUSDT 加阈值+宽止损
- entry_threshold=0.5, atr_stop=5.0
- Sharpe -0.54, 收益 -38%, MaxDD -45%, 3905笔
- ❌ 更差

## v3 (2026-05-31) — BNBUSDT 短窗口
- windows [20,40,80,160], atr_stop=5.0
- Sharpe -0.66, 收益 -0.46%, MaxDD -0.56%, 3556笔
- ❌ 基本打平但负 Sharpe

## 结论: Discard
信号在加密单标的上无预测力。原文 62 合约分散化是关键，单标的简化版不可行。

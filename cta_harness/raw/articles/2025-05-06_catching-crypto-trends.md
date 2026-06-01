# Catching Crypto Trends: A Tactical Approach for Bitcoin and Altcoins

**Authors**: Carlo Zarattini, Alberto Pagani, Andrea Barbon
**Source**: Concretum Group (Substack + SSRN)
**Date**: May 6, 2025
**SSRN**: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5209907

## Summary

将经典趋势跟踪方法（Donchian Channel 突破）应用于加密市场。使用 9 个不同回溯期的 Donchian 通道集成模型 + 波动率目标仓位管理。

## Key Strategy Components

1. **Entry**: Buy when close breaks above DonchianUp_n (upper Donchian channel on close prices)
2. **Exit (Trailing Stop)**: Close when price falls below DonchianMid_n trailing stop (never moved downward)
3. **Ensemble**: 9 lookback periods (5, 10, 20, 30, 60, 90, 150, 250, 360 days), equal-weighted average
4. **Position Sizing**: Volatility targeting — w_t = min(0.25 / σ_90d, 200%), σ = 90-day annualized vol

## Performance (BTC 2015-2025)
- Net-of-fees Sharpe > 1.5
- CAGR 30%
- Max Drawdown 19%
- Annualized alpha 10.8% vs Bitcoin

## Performance (Top-20 Crypto Rotation)
- Net-of-fees CAGR 18%
- Max Drawdown 11%
- Low correlation (~7.4%) with SG Trend Index

## Potential Strategy Directions

1. **Donchian Ensemble Trend (core)**: 9-lookback Donchian ensemble + volatility targeting + trailing midpoint stop
2. **Reduced Ensemble**: 3-5 lookback periods for faster computation / lower lookback requirements
3. **Scaled-down version**: Replace daily bars with 4h/1h bars with adjusted lookback periods
4. **Fixed-size version**: Same ensemble with fixed position size (remove vol targeting) for baseline comparison

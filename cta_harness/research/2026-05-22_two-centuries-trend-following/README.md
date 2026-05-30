# Two Centuries Trend Following 研究项目

**来源：** [wiki/sources/two-centuries-trend-following.md](../../wiki/sources/two-centuries-trend-following.md)
**日期：** 2026-05-22
**状态：** ❌ 已关闭 (Discard — 预验证失败)

---

## 最终结论

**决策：Discard** — CFM波动率归一化EMA偏离趋势信号未通过预验证。

### 原因
- 日频和月频方向准确率均<55%
- 与TSMOM预验证结论一致：月频时间序列动量在中国商品期货上不显著
- 样本仅5年（60~62个月度数据点），可能不足以检测该效应
- 详见 [iterations.md](iterations.md)

### 教训
CFM论文信号在rb99/j99/i99/jm99上无显著预测能力。

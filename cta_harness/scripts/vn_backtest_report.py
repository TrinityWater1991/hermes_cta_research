#!/usr/bin/env python3
"""vn-backtest-report: 基于回测结果生成HTML报告.

支持从stdin/文件读取回测JSON，或直接运行回测后生成报告.
报告包含统计指标表格和Plotly图表（净值、回撤、每日盈亏、盈亏分布）.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
import numpy as np
from pandas import DataFrame
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# 依赖vnpy框架
try:
    from vnpy.trader.constant import Interval, Exchange
    from vnpy_ctastrategy.backtesting import BacktestingEngine
    from vnpy_ctastrategy.base import BacktestingMode
    from vnpy_ctastrategy.template import CtaTemplate
except ImportError as e:
    print(f"错误: 未找到vnpy_ctastrategy: {e}")
    sys.exit(1)


STRATEGIES_DIR = Path(__file__).parent.parent / "strategies"

REPORT_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>{title}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: #fff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 2px solid #4a90d9; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .meta {{ color: #888; margin-bottom: 20px; }}
        table.stats {{ width: 100%%; border-collapse: collapse; margin: 20px 0; }}
        table.stats th, table.stats td {{ padding: 10px 14px; text-align: left; border-bottom: 1px solid #e0e0e0; }}
        table.stats th {{ background: #f8f9fa; font-weight: 600; color: #444; }}
        table.stats td {{ color: #333; }}
        table.stats tr:hover {{ background: #f8f9fa; }}
        .highlight {{ color: #4a90d9; font-weight: 600; }}
        .positive {{ color: #d32f2f; }}
        .negative {{ color: #388e3c; }}
        .chart-container {{ margin-top: 30px; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="meta">{meta}</div>
        <h2>统计指标</h2>
        <table class="stats">
            <tr><th>指标</th><th>数值</th></tr>
            {stats_rows}
        </table>
        <h2>图表分析</h2>
        <div class="chart-container">
            {chart}
        </div>
    </div>
</body>
</html>
"""


def load_strategy_class(strategy_name: str) -> type[CtaTemplate]:
    """加载策略类: 先尝试用户自定义策略，再尝试vnpy内置策略."""

    def _camel_to_snake(name: str) -> str:
        name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    strategy_file = STRATEGIES_DIR / f"{strategy_name}.py"
    if not strategy_file.exists():
        strategy_file = STRATEGIES_DIR / f"{_camel_to_snake(strategy_name)}.py"

    if strategy_file.exists():
        module_name = f"strategies.{strategy_name}"
        spec = importlib.util.spec_from_file_location(module_name, strategy_file)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    else:
        snake_name = _camel_to_snake(strategy_name)
        try:
            module = importlib.import_module(f"vnpy_ctastrategy.strategies.{snake_name}")
        except ImportError:
            click.echo(f"错误: 未找到策略 {strategy_name} (尝试模块: {snake_name})", err=True)
            sys.exit(1)

    candidates = []
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, CtaTemplate) and attr is not CtaTemplate:
            candidates.append(attr)

    if not candidates:
        click.echo("错误: 未找到CtaTemplate子类", err=True)
        sys.exit(1)

    for c in candidates:
        if c.__name__.lower() == strategy_name.lower():
            return c
    return candidates[0]


def _fmt(v) -> str:
    """格式化统计值."""
    if isinstance(v, float):
        return f"{v:,.4f}"
    if isinstance(v, int):
        return f"{v:,}"
    return str(v)


def build_stats_rows(stats: dict) -> str:
    """生成统计指标HTML行."""
    key_labels = [
        ("开始日期", "start_date"),
        ("结束日期", "end_date"),
        ("总交易日", "total_days"),
        ("盈利日", "profit_days"),
        ("亏损日", "loss_days"),
        ("起始资金", "capital"),
        ("结束资金", "end_balance"),
        ("总收益率", "total_return"),
        ("年化收益率", "annual_return"),
        ("最大回撤(金额)", "max_drawdown"),
        ("最大回撤(百分比)", "max_ddpercent"),
        ("最大回撤天数", "max_drawdown_duration"),
        ("净盈亏", "total_net_pnl"),
        ("手续费", "total_commission"),
        ("滑点", "total_slippage"),
        ("成交金额", "total_turnover"),
        ("总成交笔数", "total_trade_count"),
        ("日均盈亏", "daily_net_pnl"),
        ("日均收益率", "daily_return"),
        ("收益标准差", "return_std"),
        ("夏普比率", "sharpe_ratio"),
        ("EWM 夏普", "ewm_sharpe"),
        ("收益回撤比", "return_drawdown_ratio"),
        ("RGR比率", "rgr_ratio"),
    ]
    rows = []
    for label, key in key_labels:
        v = stats.get(key, "N/A")
        cls = ""
        if key in ("total_return", "annual_return", "total_net_pnl", "daily_net_pnl", "daily_return"):
            try:
                cls = "positive" if float(v) > 0 else "negative" if float(v) < 0 else ""
            except (TypeError, ValueError):
                pass
        rows.append(f'<tr><td>{label}</td><td class="{cls}">{_fmt(v)}</td></tr>')
    return "\n".join(rows)


def create_chart_figure(df: DataFrame) -> go.Figure:
    """基于daily_df创建Plotly图表."""
    fig = make_subplots(
        rows=4, cols=1,
        subplot_titles=["账户净值", "净值回撤", "每日盈亏", "盈亏分布"],
        vertical_spacing=0.08,
    )

    # Balance
    fig.add_trace(go.Scatter(
        x=df.index, y=df["balance"],
        mode="lines", name="净值", line=dict(color="#4a90d9")
    ), row=1, col=1)

    # Drawdown
    fig.add_trace(go.Scatter(
        x=df.index, y=df["drawdown"],
        fill="tozeroy", mode="lines", name="回撤",
        line=dict(color="#e74c3c"), fillcolor="rgba(231,76,60,0.3)"
    ), row=2, col=1)

    # Daily Pnl
    colors = ["#e74c3c" if x > 0 else "#27ae60" for x in df["net_pnl"]]
    fig.add_trace(go.Bar(
        x=df.index, y=df["net_pnl"],
        name="每日盈亏", marker_color=colors
    ), row=3, col=1)

    # Pnl Distribution
    fig.add_trace(go.Histogram(
        x=df["net_pnl"], nbinsx=50,
        name="盈亏分布", marker_color="#9b59b6"
    ), row=4, col=1)

    fig.update_layout(
        height=1200, width=1000,
        showlegend=False,
        title_text="回测业绩图表",
        template="plotly_white",
    )
    fig.update_xaxes(rangeslider_visible=False)
    return fig


def run_backtest(
    symbol: str,
    interval: Interval,
    start: datetime,
    end: datetime,
    strategy_class: type[CtaTemplate],
    setting: dict,
    capital: int = 1_000_000,
    size: float = 10,
    rate: float = 0.0001,
    slippage: float = 1.0,
    pricetick: float = 1.0,
) -> tuple[dict, DataFrame]:
    """运行回测，返回statistics和daily_df."""
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol=symbol,
        interval=interval,
        start=start,
        end=end,
        rate=rate,
        slippage=slippage,
        size=size,
        pricetick=pricetick,
        capital=capital,
        mode=BacktestingMode.BAR,
    )
    engine.add_strategy(strategy_class, setting)
    engine.load_data()
    if not engine.history_data:
        raise ValueError("未找到历史数据")
    engine.run_backtesting()
    engine.calculate_result()
    stats = engine.calculate_statistics(output=False)
    return stats, engine.daily_df


def generate_report(
    symbol: str,
    strategy: str,
    setting: dict,
    stats: dict,
    daily_df: DataFrame | None,
    output_path: str,
) -> None:
    """生成HTML报告."""
    title = f"回测报告: {strategy} | {symbol}"
    meta = (
        f"合约: {symbol} | 策略: {strategy} | "
        f"参数: {setting} | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    stats_rows = build_stats_rows(stats)

    if daily_df is not None and not daily_df.empty:
        fig = create_chart_figure(daily_df)
        chart_html = fig.to_html(full_html=False, include_plotlyjs="cdn")
    else:
        chart_html = "<p>无每日盈亏数据，无法生成图表</p>"

    html = REPORT_TEMPLATE.format(
        title=title,
        meta=meta,
        stats_rows=stats_rows,
        chart=chart_html,
    )

    Path(output_path).write_text(html, encoding="utf-8")
    click.echo(f"报告已保存: {output_path}")


@click.command()
@click.option("--stdin", is_flag=True, help="从stdin读取回测JSON")
@click.option("--input", "input_file", help="从文件读取回测JSON")
@click.option("-s", "--symbol", help="合约代码，如 rb99.SHFE（直接运行时需要）")
@click.option("-c", "--class_name", "strategy_class_name", help="策略类名（直接运行时需要）")
@click.option("-i", "--interval", default="1m", help="数据周期: 1m/1h/d")
@click.option("-S", "--start", help="开始日期: YYYY-MM-DD")
@click.option("-E", "--end", help="结束日期: YYYY-MM-DD")
@click.option("-p", "--param", multiple=True, help="策略参数，格式 key=value")
@click.option("--capital", default=1_000_000, help="回测资金")
@click.option("--size", default=10, help="合约乘数")
@click.option("--rate", default=0.0001, help="手续费率")
@click.option("--slippage", default=1.0, help="滑点")
@click.option("--pricetick", default=1.0, help="最小变动价位")
@click.option("-o", "--output", required=True, help="输出HTML文件路径")
def main(
    stdin: bool,
    input_file: Optional[str],
    symbol: Optional[str],
    strategy_class_name: Optional[str],
    interval: str,
    start: Optional[str],
    end: Optional[str],
    param: tuple,
    capital: int,
    size: float,
    rate: float,
    slippage: float,
    pricetick: float,
    output: str,
) -> None:
    """生成CTA回测HTML报告.

    示例:
        python vn_backtest_report.py -s rb99.SHFE -c AtrRsiStrategy -i 1m -S 2020-01-01 -o report.html
        python vn_backtest_run.py -s rb99.SHFE ... --output json | python vn_backtest_report.py --stdin -o report.html
    """
    stats: dict = {}
    daily_df: DataFrame | None = None
    setting: dict = {}

    # 模式1: 从stdin或文件读取
    if stdin or input_file:
        if stdin:
            data = json.load(click.get_text_stream("stdin"))
        else:
            data = json.loads(Path(input_file).read_text(encoding="utf-8"))

        symbol = data.get("symbol", symbol)
        strategy_class_name = data.get("strategy", strategy_class_name)
        stats = data.get("stats", {})
        setting = data.get("setting", {})

        # 如果JSON中包含daily数据
        daily_raw = data.get("daily")
        if daily_raw:
            daily_df = DataFrame(daily_raw)
            if "date" in daily_df.columns:
                daily_df["date"] = daily_df["date"].astype(str)
                daily_df.set_index("date", inplace=True)

    # 模式2: 直接运行回测
    if not stats and symbol and strategy_class_name and start:
        if "." not in symbol:
            click.echo("错误: symbol格式应为 'code.exchange'", err=True)
            sys.exit(1)

        start_dt = datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.strptime(end, "%Y-%m-%d") if end else datetime.now()

        interval_map = {
            "1m": Interval.MINUTE, "1min": Interval.MINUTE, "min": Interval.MINUTE,
            "1h": Interval.HOUR, "h": Interval.HOUR,
            "d": Interval.DAILY, "1d": Interval.DAILY, "day": Interval.DAILY,
        }
        vnpy_interval = interval_map.get(interval, Interval.MINUTE)

        # 解析参数
        for p in param:
            if "=" not in p:
                continue
            k, v = p.split("=", 1)
            try:
                v = int(v)
            except ValueError:
                try:
                    v = float(v)
                except ValueError:
                    pass
            setting[k] = v

        strategy_class = load_strategy_class(strategy_class_name)
        stats, daily_df = run_backtest(
            symbol=symbol,
            interval=vnpy_interval,
            start=start_dt,
            end=end_dt,
            strategy_class=strategy_class,
            setting=setting,
            capital=capital,
            size=size,
            rate=rate,
            slippage=slippage,
            pricetick=pricetick,
        )

    if not stats:
        click.echo("错误: 无法获取回测结果，请提供symbol+class_name+start或有效的JSON输入", err=True)
        sys.exit(1)

    generate_report(
        symbol=symbol or "unknown",
        strategy=strategy_class_name or "unknown",
        setting=setting,
        stats=stats,
        daily_df=daily_df,
        output_path=output,
    )


if __name__ == "__main__":
    main()

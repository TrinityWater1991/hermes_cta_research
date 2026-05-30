#!/usr/bin/env python3
"""vn-backtest-run: 运行CTA策略回测.

使用vnpy BacktestingEngine，支持动态加载策略。
"""

from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

# 依赖vnpy框架
try:
    from vnpy.trader.constant import Interval, Exchange
    from vnpy_ctastrategy.backtesting import BacktestingEngine
    from vnpy_ctastrategy.base import BacktestingMode
    from vnpy_ctastrategy.template import CtaTemplate
except ImportError as e:
    print(f"错误: 未找到vnpy_ctastrategy: {e}")
    sys.exit(1)


console = Console()
STRATEGIES_DIR = Path(__file__).parent.parent / "strategies"


def load_strategy_class(strategy_name: str) -> type[CtaTemplate]:
    """从策略目录动态加载策略类."""
    strategy_file = STRATEGIES_DIR / f"{strategy_name}.py"
    if not strategy_file.exists():
        console.print(f"[red]策略文件不存在: {strategy_file}[/red]")
        sys.exit(1)

    module_name = f"strategies.{strategy_name}"
    spec = importlib.util.spec_from_file_location(module_name, strategy_file)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    # 查找CtaTemplate子类
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, CtaTemplate) and attr is not CtaTemplate:
            return attr

    console.print("[red]未在策略文件中找到CtaTemplate子类[/red]")
    sys.exit(1)


@click.command()
@click.option("-s", "--symbol", required=True, help="合约代码，如 rb99.SHFE")
@click.option("-i", "--interval", default="1m", help="数据周期: 1m/1h/d")
@click.option("-S", "--start", required=True, help="开始日期: YYYY-MM-DD")
@click.option("-e", "--end", help="结束日期: YYYY-MM-DD，默认今天")
@click.option("--strategy", default="double_ma_strategy", help="策略文件名（不含.py）")
@click.option("--capital", default=1_000_000, help="初始资金，默认100万")
@click.option("--size", default=10, help="合约乘数，默认10")
@click.option("--rate", default=0.0001, help="手续费率，默认0.01%")
@click.option("--slippage", default=1.0, help="滑点，默认1")
@click.option("--pricetick", default=1.0, help="最小变动价位，默认1")
@click.option("-p", "--param", multiple=True, help="策略参数，格式 key=value")
@click.option("-o", "--output", type=click.Choice(["table", "json"]), default="table", help="输出格式")
@click.option("-q", "--quiet", is_flag=True, help="静默模式")
def main(
    symbol: str,
    interval: str,
    start: str,
    end: Optional[str],
    strategy: str,
    capital: int,
    size: float,
    rate: float,
    slippage: float,
    pricetick: float,
    param: tuple,
    output: str,
    quiet: bool,
) -> None:
    """运行CTA策略回测.

    示例:
        python vn_backtest_run.py -s rb99.SHFE -i 1m -S 2020-01-01 -e 2024-12-31
        python vn_backtest_run.py -s rb99.SHFE -i 1m -S 2020-01-01 --strategy double_ma_strategy -p fast_window=10 -p slow_window=60
    """
    # 解析symbol
    if "." not in symbol:
        console.print("[red]错误: symbol格式应为 'code.exchange'，如 rb99.SHFE[/red]")
        sys.exit(1)

    # 解析日期
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt = datetime.strptime(end, "%Y-%m-%d") if end else datetime.now()

    # 解析interval
    interval_map = {
        "1m": Interval.MINUTE, "1min": Interval.MINUTE, "min": Interval.MINUTE,
        "1h": Interval.HOUR, "h": Interval.HOUR,
        "d": Interval.DAILY, "1d": Interval.DAILY, "day": Interval.DAILY,
    }
    vnpy_interval = interval_map.get(interval, Interval.MINUTE)

    # 解析策略参数
    setting: dict = {}
    for p in param:
        if "=" not in p:
            console.print(f"[red]错误: 参数格式应为 key=value: {p}[/red]")
            sys.exit(1)
        k, v = p.split("=", 1)
        # 尝试转换为数字
        try:
            v = int(v)
        except ValueError:
            try:
                v = float(v)
            except ValueError:
                pass
        setting[k] = v

    if not quiet:
        console.print(f"[blue]回测: {symbol} {interval} | 策略: {strategy} | 参数: {setting}[/blue]")

    # 加载策略类
    strategy_class = load_strategy_class(strategy)

    # 创建回测引擎
    engine = BacktestingEngine()
    engine.set_parameters(
        vt_symbol=symbol,
        interval=vnpy_interval,
        start=start_dt,
        end=end_dt,
        rate=rate,
        slippage=slippage,
        size=size,
        pricetick=pricetick,
        capital=capital,
        mode=BacktestingMode.BAR,
    )

    engine.add_strategy(strategy_class, setting)

    # 加载数据并运行回测
    if not quiet:
        console.print("[blue]加载数据中...[/blue]")
    engine.load_data()

    if not engine.history_data:
        console.print("[red]未找到历史数据，请先使用 vn_data_fetch.py 下载数据[/red]")
        sys.exit(1)

    if not quiet:
        console.print(f"[blue]历史数据: {len(engine.history_data)} 条，开始回测...[/blue]")

    engine.run_backtesting()
    engine.calculate_result()

    if not quiet:
        console.print("[blue]计算统计指标...[/blue]")
    stats = engine.calculate_statistics(output=False)

    if not stats:
        console.print("[red]回测结果为空[/red]")
        sys.exit(1)

    trades = engine.get_all_trades()

    if output == "table":
        table = Table(title=f"回测结果: {symbol} | {strategy}")
        table.add_column("指标", style="cyan")
        table.add_column("数值", style="yellow")

        key_labels = {
            "start_date": "开始日期",
            "end_date": "结束日期",
            "total_days": "总天数",
            "profit_days": "盈利天数",
            "loss_days": "亏损天数",
            "end_balance": "结束资金",
            "max_drawdown": "最大回撤(金额)",
            "max_ddpercent": "最大回撤(百分比)",
            "total_net_pnl": "净盈亏",
            "total_commission": "手续费",
            "total_slippage": "滑点损失",
            "total_turnover": "成交金额",
            "total_trade_count": "总成交笔数",
            "total_return": "总收益率",
            "annual_return": "年化收益率",
            "sharpe_ratio": "夏普比率",
            "return_drawdown_ratio": "收益回撤比",
        }

        for key, label in key_labels.items():
            value = stats.get(key, "N/A")
            if isinstance(value, float):
                value = f"{value:.4f}"
            table.add_row(label, str(value))

        table.add_row("成交笔数(详细)", str(len(trades)))
        console.print(table)

    elif output == "json":
        result = {
            "symbol": symbol,
            "interval": interval,
            "strategy": strategy,
            "setting": setting,
            "stats": stats,
            "trade_count": len(trades),
        }
        click.echo(json.dumps(result, ensure_ascii=False, indent=2, default=str))


if __name__ == "__main__":
    main()

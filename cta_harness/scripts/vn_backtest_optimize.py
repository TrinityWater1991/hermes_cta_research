#!/usr/bin/env python3
"""vn-backtest-optimize: CTA策略参数优化.

基于vnpy BacktestingEngine，支持穷举（Brute Force）和遗传算法（GA）两种优化方式.
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
from rich.console import Console
from rich.table import Table

# 依赖vnpy框架
try:
    from vnpy.trader.constant import Interval, Exchange
    from vnpy.trader.optimize import OptimizationSetting
    from vnpy_ctastrategy.backtesting import BacktestingEngine
    from vnpy_ctastrategy.base import BacktestingMode
    from vnpy_ctastrategy.template import CtaTemplate
except ImportError as e:
    print(f"错误: 未找到vnpy_ctastrategy: {e}")
    sys.exit(1)


console = Console()
STRATEGIES_DIR = Path(__file__).parent.parent / "strategies"

TARGET_CHOICES = [
    "total_return",
    "annual_return",
    "sharpe_ratio",
    "ewm_sharpe",
    "max_drawdown",
    "max_ddpercent",
    "return_drawdown_ratio",
    "rgr_ratio",
    "total_net_pnl",
    "daily_net_pnl",
    "total_trade_count",
    "daily_trade_count",
]


def load_strategy_class(strategy_name: str) -> type[CtaTemplate]:
    """加载策略类: 先尝试用户自定义策略，再尝试vnpy内置策略."""

    def _camel_to_snake(name: str) -> str:
        name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()

    # 1. 尝试从用户策略目录加载
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
        # 2. 尝试从vnpy_ctastrategy内置策略加载
        snake_name = _camel_to_snake(strategy_name)
        try:
            module = importlib.import_module(f"vnpy_ctastrategy.strategies.{snake_name}")
        except ImportError:
            console.print(f"[red]未找到策略: {strategy_name} (尝试模块: {snake_name})[/red]")
            sys.exit(1)

    # 查找CtaTemplate子类
    candidates = []
    for attr_name in dir(module):
        attr = getattr(module, attr_name)
        if isinstance(attr, type) and issubclass(attr, CtaTemplate) and attr is not CtaTemplate:
            candidates.append(attr)

    if not candidates:
        console.print("[red]未在策略文件中找到CtaTemplate子类[/red]")
        sys.exit(1)

    # 如果有多个，尝试匹配类名
    for c in candidates:
        if c.__name__.lower() == strategy_name.lower():
            return c
    return candidates[0]


def _to_serializable(obj):
    """将numpy类型和其他非序列化类型转换为Python原生类型."""
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, (np.integer, np.floating)):
        return float(obj)
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def clean_statistics(stats: dict) -> dict:
    """清理statistics中的非序列化值."""
    cleaned = {}
    for k, v in stats.items():
        if isinstance(v, dict):
            cleaned[k] = clean_statistics(v)
        else:
            cleaned[k] = _to_serializable(v)
    return cleaned


@click.command()
@click.option("-c", "--class_name", "strategy_class_name", required=True, help="策略类名，如 AtrRsiStrategy")
@click.option("-s", "--symbol", required=True, help="合约代码，如 rb99.SHFE")
@click.option("-i", "--interval", default="1m", help="数据周期: 1m/1h/d")
@click.option("-S", "--start", required=True, help="开始日期: YYYY-MM-DD")
@click.option("-E", "--end", help="结束日期: YYYY-MM-DD，默认今天")
@click.option("--param", multiple=True, required=True, help="优化参数，格式 name:start:end:step，可多次指定")
@click.option("--method", type=click.Choice(["bf", "ga"]), default="bf", help="优化方法: bf=穷举, ga=遗传")
@click.option("--target", type=click.Choice(TARGET_CHOICES), default="sharpe_ratio", help="优化目标")
@click.option("--workers", default=-1, help="并行进程数，-1=全部CPU")
@click.option("--capital", default=1_000_000, help="回测资金，默认100万")
@click.option("--size", default=10, help="合约乘数")
@click.option("--rate", default=0.0001, help="手续费率")
@click.option("--slippage", default=1.0, help="滑点")
@click.option("--pricetick", default=1.0, help="最小变动价位")
@click.option("--ga-pop", default=100, help="GA种群大小（仅ga有效）")
@click.option("--ga-ngen", default=30, help="GA迭代代数（仅ga有效）")
@click.option("--ga-cxpb", default=0.95, help="GA交叉概率（仅ga有效）")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="json", help="输出格式")
@click.option("-o", "--output", "output_file", help="结果保存文件路径")
@click.option("--quiet", is_flag=True, help="静默模式")
def main(
    strategy_class_name: str,
    symbol: str,
    interval: str,
    start: str,
    end: Optional[str],
    param: tuple,
    method: str,
    target: str,
    workers: int,
    capital: int,
    size: float,
    rate: float,
    slippage: float,
    pricetick: float,
    ga_pop: int,
    ga_ngen: int,
    ga_cxpb: float,
    fmt: str,
    output_file: Optional[str],
    quiet: bool,
) -> None:
    """执行CTA策略参数优化.

    示例:
        python vn_backtest_optimize.py -c AtrRsiStrategy -s rb99.SHFE -i 1m -S 2020-01-01 --method bf \\
            --param atr_length:10:30:5 --param atr_ma_length:10:30:5 --target sharpe_ratio

        python vn_backtest_optimize.py -c AtrRsiStrategy -s rb99.SHFE -i 1m -S 2020-01-01 --method ga \\
            --param atr_length:5:50:1 --param atr_ma_length:5:50:1 --target total_return
    """
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

    # 解析优化参数
    opt_setting = OptimizationSetting()
    opt_setting.set_target(target)

    for p in param:
        parts = p.split(":")
        if len(parts) != 4:
            console.print(f"[red]错误: 参数格式应为 name:start:end:step, 得到: {p}[/red]")
            sys.exit(1)
        name, start_v, end_v, step_v = parts
        try:
            start_v = float(start_v)
            end_v = float(end_v)
            step_v = float(step_v)
        except ValueError:
            console.print(f"[red]错误: 参数值必须为数字: {p}[/red]")
            sys.exit(1)

        # 尝试转为整数（如果都是整数）
        if start_v == int(start_v) and end_v == int(end_v) and step_v == int(step_v):
            start_v, end_v, step_v = int(start_v), int(end_v), int(step_v)

        success, msg = opt_setting.add_parameter(name, start_v, end_v, step_v)
        if not success:
            console.print(f"[red]参数配置错误 ({name}): {msg}[/red]")
            sys.exit(1)

    # 计算workers
    max_workers = None if workers == -1 else workers

    if not quiet:
        console.print(f"[blue]优化: {symbol} | 策略: {strategy_class_name} | 方法: {method} | 目标: {target}[/blue]")
        settings_list = opt_setting.generate_settings()
        console.print(f"[blue]参数空间: {len(settings_list)} 种组合 | 并行: {workers}[/blue]")

    # 加载策略类
    strategy_class = load_strategy_class(strategy_class_name)

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

    # 添加策略（用于确定类，优化过程会使用不同参数）
    engine.add_strategy(strategy_class, {})

    # 检查参数
    if not quiet:
        console.print("[blue]开始优化...[/blue]")

    # 执行优化
    if method == "bf":
        results = engine.run_bf_optimization(
            optimization_setting=opt_setting,
            output=not quiet,
            max_workers=max_workers,
        )
    else:
        results = engine.run_ga_optimization(
            optimization_setting=opt_setting,
            output=not quiet,
            max_workers=max_workers,
            pop_size=ga_pop,
            ngen=ga_ngen,
            cxpb=ga_cxpb,
        )

    if not results:
        console.print("[red]优化未返回结果[/red]")
        sys.exit(1)

    # 构建输出
    output_results = []
    for rank, result in enumerate(results, start=1):
        setting_dict = result[0]
        target_value = float(result[1])
        stats = result[2] if len(result) > 2 else {}
        output_results.append({
            "rank": rank,
            "params": setting_dict,
            "target_value": target_value,
            "statistics": clean_statistics(stats) if isinstance(stats, dict) else {},
        })

    meta = {
        "strategy": strategy_class_name,
        "symbol": symbol,
        "interval": interval,
        "start": start,
        "end": end_dt.strftime("%Y-%m-%d"),
        "method": method,
        "target": target,
        "total_combinations_evaluated": len(results),
    }

    if fmt == "table":
        table = Table(title=f"参数优化结果: {strategy_class_name} | {symbol} | 目标: {target}")
        table.add_column("Rank", style="cyan", justify="right")
        table.add_column("Params", style="green")
        table.add_column("Target", style="yellow", justify="right")
        table.add_column("TotalReturn", justify="right")
        table.add_column("Sharpe", justify="right")
        table.add_column("MaxDD%", justify="right")
        table.add_column("Trades", justify="right")

        for r in output_results[:20]:  # 只显示前20
            stats = r["statistics"]
            params_str = ", ".join(f"{k}={v}" for k, v in r["params"].items())
            table.add_row(
                str(r["rank"]),
                params_str,
                f"{r['target_value']:.4f}",
                f"{stats.get('total_return', 0):.2f}%",
                f"{stats.get('sharpe_ratio', 0):.2f}",
                f"{stats.get('max_ddpercent', 0):.2f}%",
                str(stats.get('total_trade_count', 0)),
            )
        console.print(table)
        if len(output_results) > 20:
            console.print(f"[dim]共 {len(output_results)} 组结果，仅显示前20[/dim]")

    elif fmt == "json":
        result_json = {
            "meta": meta,
            "results": output_results,
        }
        json_str = json.dumps(result_json, ensure_ascii=False, indent=2, default=str)
        if output_file:
            Path(output_file).write_text(json_str, encoding="utf-8")
            if not quiet:
                console.print(f"[green]结果已保存至: {output_file}[/green]")
        else:
            click.echo(json_str)


if __name__ == "__main__":
    main()

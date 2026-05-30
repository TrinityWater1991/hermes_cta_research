#!/usr/bin/env python3
"""vn-data-overview: 查询数据库中的数据资产概览.

使用 vnpy.database.get_database().get_bar_overview() API，
展示本地数据库中所有K线/Tick数据的覆盖范围、记录数等信息.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

# 依赖vnpy框架
try:
    from vnpy.trader.database import get_database
except ImportError as e:
    print(f"错误: 未找到vnpy: {e}")
    sys.exit(1)


console = Console()


# 各周期每交易日大致预期条数（用于缺口估算）
INTERVAL_EXPECTED_PER_DAY: dict[str, int] = {
    "1m": 240,
    "5m": 48,
    "15m": 16,
    "1h": 4,
    "d": 1,
    "w": 1,
}


def _fmt_dt(dt: Optional[datetime]) -> str:
    """格式化日期时间."""
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def _vt_symbol(symbol: str, exchange) -> str:
    """构造vt_symbol."""
    ex = exchange.value if exchange else ""
    return f"{symbol}.{ex}"


@click.command()
@click.option("-s", "--symbol", help="过滤合约代码，如 rb99")
@click.option("--exchange", help="过滤交易所，如 SHFE")
@click.option("-i", "--interval", help="过滤周期: 1m/5m/15m/1h/d/w")
@click.option("--format", "fmt", type=click.Choice(["table", "json"]), default="table", help="输出格式")
@click.option("--gaps", is_flag=True, help="检测数据缺口（基于记录数估算）")
@click.option("--min-gap-days", default=1, help="缺口检测最小缺失天数，默认1")
@click.option("--tick", is_flag=True, help="同时显示Tick数据概览")
def main(
    symbol: Optional[str],
    exchange: Optional[str],
    interval: Optional[str],
    fmt: str,
    gaps: bool,
    min_gap_days: int,
    tick: bool,
) -> None:
    """查询数据库中的数据资产概览.

    示例:
        python vn_data_overview.py
        python vn_data_overview.py -s rb99 --exchange SHFE
        python vn_data_overview.py --gaps --format json
    """
    db = get_database()

    # 获取Bar概览
    bar_overviews = db.get_bar_overview()
    # 获取Tick概览
    tick_overviews = db.get_tick_overview() if tick else []

    # 过滤Bar
    bars = []
    for ov in bar_overviews:
        if symbol and ov.symbol != symbol:
            continue
        if exchange and ov.exchange and ov.exchange.value != exchange:
            continue
        if interval and ov.interval and ov.interval.value != interval:
            continue
        bars.append(ov)

    # 过滤Tick
    ticks = []
    for ov in tick_overviews:
        if symbol and ov.symbol != symbol:
            continue
        if exchange and ov.exchange and ov.exchange.value != exchange:
            continue
        ticks.append(ov)

    if fmt == "table":
        # Bar表格
        if bars:
            table = Table(title=f"数据库Bar数据概览 (共 {len(bars)} 组)")
            table.add_column("Symbol", style="cyan", no_wrap=True)
            table.add_column("Exchange", style="blue")
            table.add_column("Interval", style="green")
            table.add_column("Start", style="magenta")
            table.add_column("End", style="magenta")
            table.add_column("Count", style="yellow", justify="right")
            table.add_column("Coverage", style="dim")

            for ov in bars:
                interval_str = ov.interval.value if ov.interval else "?"
                start_str = _fmt_dt(ov.start)
                end_str = _fmt_dt(ov.end)
                count_str = f"{ov.count:,}" if ov.count else "0"

                # 估算覆盖率
                coverage = ""
                if ov.start and ov.end and ov.count:
                    days = (ov.end - ov.start).days + 1
                    expected = INTERVAL_EXPECTED_PER_DAY.get(interval_str, 0) * max(days, 1)
                    if expected > 0:
                        ratio = ov.count / expected
                        if ratio >= 0.95:
                            coverage = f"[green]{ratio:.1%}[/green]"
                        elif ratio >= 0.7:
                            coverage = f"[yellow]{ratio:.1%}[/yellow]"
                        else:
                            coverage = f"[red]{ratio:.1%}[/red]"
                table.add_row(
                    ov.symbol,
                    ov.exchange.value if ov.exchange else "",
                    interval_str,
                    start_str,
                    end_str,
                    count_str,
                    coverage,
                )
            console.print(table)
        else:
            console.print("[yellow]未找到匹配的Bar数据[/yellow]")

        # Tick表格
        if ticks:
            ttable = Table(title=f"数据库Tick数据概览 (共 {len(ticks)} 组)")
            ttable.add_column("Symbol", style="cyan")
            ttable.add_column("Exchange", style="blue")
            ttable.add_column("Start", style="magenta")
            ttable.add_column("End", style="magenta")
            ttable.add_column("Count", style="yellow", justify="right")
            for ov in ticks:
                ttable.add_row(
                    ov.symbol,
                    ov.exchange.value if ov.exchange else "",
                    _fmt_dt(ov.start),
                    _fmt_dt(ov.end),
                    f"{ov.count:,}" if ov.count else "0",
                )
            console.print(ttable)

        # 缺口检测
        if gaps and bars:
            gap_found = False
            gtable = Table(title="数据缺口检测（基于记录数估算）")
            gtable.add_column("Symbol", style="cyan")
            gtable.add_column("Interval", style="green")
            gtable.add_column("Start", style="magenta")
            gtable.add_column("End", style="magenta")
            gtable.add_column("Expected", justify="right")
            gtable.add_column("Actual", justify="right")
            gtable.add_column("MissingDays", justify="right", style="red")

            for ov in bars:
                interval_str = ov.interval.value if ov.interval else "?"
                if not ov.start or not ov.end or not ov.count:
                    continue
                days = (ov.end - ov.start).days + 1
                per_day = INTERVAL_EXPECTED_PER_DAY.get(interval_str, 0)
                if per_day == 0:
                    continue
                expected = per_day * days
                if expected <= 0:
                    continue
                missing_records = expected - ov.count
                missing_days = missing_records / per_day
                if missing_days >= min_gap_days:
                    gap_found = True
                    gtable.add_row(
                        ov.symbol,
                        interval_str,
                        _fmt_dt(ov.start),
                        _fmt_dt(ov.end),
                        f"{expected:,}",
                        f"{ov.count:,}",
                        f"{missing_days:.1f}",
                    )
            if gap_found:
                console.print(gtable)
            else:
                console.print(f"[green]未发现超过 {min_gap_days} 天的数据缺口[/green]")

    elif fmt == "json":
        # JSON输出
        bar_data = []
        for ov in bars:
            interval_str = ov.interval.value if ov.interval else None
            item = {
                "symbol": ov.symbol,
                "exchange": ov.exchange.value if ov.exchange else None,
                "interval": interval_str,
                "start": ov.start.isoformat() if ov.start else None,
                "end": ov.end.isoformat() if ov.end else None,
                "count": ov.count,
                "vt_symbol": _vt_symbol(ov.symbol, ov.exchange),
            }
            if gaps and ov.start and ov.end and ov.count:
                days = (ov.end - ov.start).days + 1
                per_day = INTERVAL_EXPECTED_PER_DAY.get(interval_str, 0) if interval_str else 0
                if per_day > 0:
                    expected = per_day * days
                    missing_days = (expected - ov.count) / per_day
                    item["expected_count"] = expected
                    item["missing_days"] = round(missing_days, 1)
            bar_data.append(item)

        tick_data = []
        for ov in ticks:
            tick_data.append({
                "symbol": ov.symbol,
                "exchange": ov.exchange.value if ov.exchange else None,
                "start": ov.start.isoformat() if ov.start else None,
                "end": ov.end.isoformat() if ov.end else None,
                "count": ov.count,
                "vt_symbol": _vt_symbol(ov.symbol, ov.exchange),
            })

        result = {
            "bars": bar_data,
            "ticks": tick_data,
            "summary": {
                "total_bar_groups": len(bar_data),
                "total_tick_groups": len(tick_data),
                "db_type": type(db).__name__,
            },
        }
        click.echo(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

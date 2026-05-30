#!/usr/bin/env python3
"""vn-data-export: 从vnpy数据库导出数据到CSV/JSON.

支持管道输出，便于与vn-data-clean、jq等工具组合。
"""

from __future__ import annotations

import csv
import json
import sys
from datetime import datetime, timedelta
from typing import List, Optional, TextIO

import click
from rich.console import Console

# 依赖vnpy框架
try:
    from vnpy.trader.database import get_database
    from vnpy.trader.object import BarData
    from vnpy.trader.constant import Exchange, Interval
except ImportError:
    console = Console()
    console.print("[red]错误: 未找到vnpy，请先安装: pip install vnpy[/red]")
    sys.exit(1)


console = Console()


def bars_to_csv(bars: List[BarData], output: TextIO) -> None:
    """BarData列表输出为CSV."""
    writer = csv.writer(output)
    writer.writerow([
        "datetime", "symbol", "exchange", "interval",
        "open", "high", "low", "close", "volume", "turnover", "open_interest",
    ])
    for b in bars:
        writer.writerow([
            b.datetime.isoformat(), b.symbol, b.exchange.value, b.interval.value,
            b.open_price, b.high_price, b.low_price, b.close_price,
            b.volume, b.turnover, b.open_interest,
        ])


def bars_to_json(bars: List[BarData], symbol: str, interval: str, output: TextIO) -> None:
    """BarData列表输出为JSON."""
    data = {
        "symbol": symbol,
        "interval": interval,
        "count": len(bars),
        "start": bars[0].datetime.isoformat() if bars else None,
        "end": bars[-1].datetime.isoformat() if bars else None,
        "data": [
            {
                "symbol": b.symbol,
                "exchange": b.exchange.value,
                "datetime": b.datetime.isoformat(),
                "interval": b.interval.value,
                "open_price": b.open_price,
                "high_price": b.high_price,
                "low_price": b.low_price,
                "close_price": b.close_price,
                "volume": b.volume,
                "turnover": b.turnover,
                "open_interest": b.open_interest,
            }
            for b in bars
        ],
    }
    json.dump(data, output, ensure_ascii=False, indent=2)
    output.write("\n")


@click.command()
@click.option("-s", "--symbol", required=True, help="合约代码，如 rb2501.SHFE")
@click.option("-i", "--interval", default="1m", help="数据周期: tick/1m/1h/d")
@click.option("-S", "--start", help="开始日期: YYYY-MM-DD，默认30天前")
@click.option("-e", "--end", help="结束日期: YYYY-MM-DD，默认今天")
@click.option("-f", "--format", "fmt", type=click.Choice(["csv", "json"]), default="csv", help="输出格式，默认csv")
@click.option("-o", "--output", type=click.File("w", encoding="utf-8"), default="-", help="输出文件，默认stdout")
@click.option("-q", "--quiet", is_flag=True, help="静默模式")
def main(
    symbol: str,
    interval: str,
    start: Optional[str],
    end: Optional[str],
    fmt: str,
    output: TextIO,
    quiet: bool,
) -> None:
    """从vnpy数据库导出数据.

    示例:
        python vn_data_export.py -s rb2501.SHFE -i 1m -S 2024-01-01 > output.csv
        python vn_data_export.py -s rb2501.SHFE -i 1m --format json | jq '.count'
        python vn_data_export.py -s rb2501.SHFE -i 1m | python vn_data_clean.py --remove-duplicates
    """
    # 解析symbol
    if "." not in symbol:
        console.print("[red]错误: symbol格式应为 'code.exchange'，如 rb2501.SHFE[/red]")
        sys.exit(1)
    code, exchange_str = symbol.split(".", 1)

    try:
        exchange = Exchange(exchange_str.upper())
    except ValueError:
        console.print(f"[red]错误: 未知交易所 {exchange_str}[/red]")
        sys.exit(1)

    # 解析interval
    interval_map = {
        "tick": Interval.TICK,
        "1m": Interval.MINUTE, "1min": Interval.MINUTE, "min": Interval.MINUTE,
        "1h": Interval.HOUR, "h": Interval.HOUR,
        "d": Interval.DAILY, "1d": Interval.DAILY, "day": Interval.DAILY,
        "w": Interval.WEEKLY, "1w": Interval.WEEKLY, "week": Interval.WEEKLY,
    }
    vnpy_interval = interval_map.get(interval, Interval.MINUTE)

    # 解析日期
    start_dt = datetime.strptime(start, "%Y-%m-%d") if start else datetime.now() - timedelta(days=30)
    end_dt = datetime.strptime(end, "%Y-%m-%d") if end else datetime.now()
    end_dt = end_dt.replace(hour=23, minute=59, second=59)

    if not quiet:
        console.print(f"[blue]导出 {symbol} {interval} 数据，范围: {start_dt.date()} 至 {end_dt.date()}...[/blue]")

    # 从数据库读取
    db = get_database()
    bars = db.load_bar_data(code, exchange, vnpy_interval, start_dt, end_dt)

    if not bars:
        if not quiet:
            console.print("[yellow]数据库中未找到数据。[/yellow]")
        sys.exit(0)

    if not quiet:
        console.print(f"[green]导出 {len(bars)} 条K线[/green]")

    # 输出
    if fmt == "csv":
        bars_to_csv(bars, output)
    else:
        bars_to_json(bars, symbol, interval, output)

    if not quiet and output.name != "<stdout>":
        console.print(f"[green]已保存到 {output.name}[/green]")


if __name__ == "__main__":
    main()

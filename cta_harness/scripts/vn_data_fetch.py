#!/usr/bin/env python3
"""vn-data-fetch: 下载历史数据并保存到vnpy数据库."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import List, Optional

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

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


def fetch_from_vnpy_datafeed(
    symbol: str,
    exchange: Exchange,
    interval: Interval,
    start: datetime,
    end: datetime,
) -> List[BarData]:
    """通过vnpy数据服务下载."""
    try:
        from vnpy.trader.datafeed import get_datafeed
        from vnpy.trader.object import HistoryRequest
        datafeed = get_datafeed()
        req = HistoryRequest(
            symbol=symbol,
            exchange=exchange,
            start=start,
            end=end,
            interval=interval,
        )
        result = datafeed.query_bar_history(req)
        return result if result else []
    except Exception as e:
        console.print(f"[yellow]vnpy数据服务下载失败: {e}[/yellow]")
        return []


def fetch_from_akshare(
    symbol: str,
    exchange: str,
    interval: str,
    start: datetime,
    end: datetime,
) -> List[BarData]:
    """通过AKShare免费下载（备用）."""
    try:
        import akshare as ak
    except ImportError:
        return []

    bars: List[BarData] = []
    exchange_upper = exchange.upper()

    # AKShare期货分钟数据
    try:
        if interval in ("1m", "1min", "min"):
            df = ak.futures_zh_minute_sina(symbol=f"{symbol}.{exchange_upper}", period="1")
        elif interval in ("5m", "5min"):
            df = ak.futures_zh_minute_sina(symbol=f"{symbol}.{exchange_upper}", period="5")
        elif interval in ("15m", "15min"):
            df = ak.futures_zh_minute_sina(symbol=f"{symbol}.{exchange_upper}", period="15")
        elif interval in ("30m", "30min"):
            df = ak.futures_zh_minute_sina(symbol=f"{symbol}.{exchange_upper}", period="30")
        elif interval in ("d", "1d", "day", "daily"):
            df = ak.futures_zh_daily_sina(symbol=f"{symbol}.{exchange_upper}")
        else:
            return []

        for _, row in df.iterrows():
            dt_str = str(row.get("datetime", row.get("date", "")))
            if not dt_str or dt_str == "nan":
                continue
            try:
                dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    dt = datetime.strptime(dt_str, "%Y-%m-%d")
                except ValueError:
                    continue

            if dt < start or dt > end:
                continue

            bar = BarData(
                symbol=symbol,
                exchange=Exchange(exchange_upper),
                datetime=dt,
                interval=Interval.MINUTE if "m" in interval else Interval.DAILY,
                volume=float(row.get("volume", 0) or 0),
                turnover=float(row.get("hold", 0) or 0) * 0,  # akshare无turnover，置0
                open_interest=float(row.get("hold", 0) or 0),
                open_price=float(row.get("open", 0) or 0),
                high_price=float(row.get("high", 0) or 0),
                low_price=float(row.get("low", 0) or 0),
                close_price=float(row.get("close", 0) or 0),
                gateway_name="DB",
            )
            bars.append(bar)
    except Exception:
        pass

    return bars


@click.command()
@click.option("-s", "--symbol", required=True, help="合约代码，如 rb2501.SHFE")
@click.option("-i", "--interval", default="1m", help="数据周期: tick/1m/5m/15m/1h/d")
@click.option("-S", "--start", required=True, help="开始日期: YYYY-MM-DD")
@click.option("-e", "--end", help="结束日期: YYYY-MM-DD，默认今天")
@click.option("--save/--no-save", default=True, help="保存到数据库，默认开启")
@click.option("-o", "--output", type=click.Choice(["json", "csv", "none"]), default="none", help="输出格式，默认不输出")
@click.option("--source", type=click.Choice(["vnpy", "akshare", "auto"]), default="auto", help="数据源，默认自动选择")
@click.option("-q", "--quiet", is_flag=True, help="静默模式")
def main(
    symbol: str,
    interval: str,
    start: str,
    end: Optional[str],
    save: bool,
    output: str,
    source: str,
    quiet: bool,
) -> None:
    """下载历史数据并保存到vnpy数据库.

    示例:
        python vn_data_fetch.py -s rb2501.SHFE -i 1m -S 2024-01-01
        python vn_data_fetch.py -s IF2501.CFFEX -i d -S 2024-01-01 -e 2024-12-31 --source akshare
        python vn_data_fetch.py -s cu2501.SHFE -i 1m -S 2024-01-01 -o json > data.json
    """
    # 解析symbol
    if "." not in symbol:
        console.print("[red]错误: symbol格式应为 'code.exchange'，如 rb2501.SHFE[/red]")
        sys.exit(1)
    code, exchange_str = symbol.split(".", 1)

    # 解析日期
    try:
        start_dt = datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        console.print("[red]错误: 开始日期格式应为 YYYY-MM-DD[/red]")
        sys.exit(1)

    end_dt = datetime.strptime(end, "%Y-%m-%d") if end else datetime.now()

    # 映射interval到vnpy Interval
    interval_map = {
        "tick": Interval.TICK,
        "1m": Interval.MINUTE, "1min": Interval.MINUTE, "min": Interval.MINUTE,
        "5m": Interval.MINUTE, "5min": Interval.MINUTE,
        "15m": Interval.MINUTE, "15min": Interval.MINUTE,
        "30m": Interval.MINUTE, "30min": Interval.MINUTE,
        "1h": Interval.HOUR, "h": Interval.HOUR, "hour": Interval.HOUR,
        "d": Interval.DAILY, "1d": Interval.DAILY, "day": Interval.DAILY, "daily": Interval.DAILY,
        "w": Interval.WEEKLY, "1w": Interval.WEEKLY, "week": Interval.WEEKLY, "weekly": Interval.WEEKLY,
    }
    vnpy_interval = interval_map.get(interval, Interval.MINUTE)

    try:
        vnpy_exchange = Exchange(exchange_str.upper())
    except ValueError:
        console.print(f"[red]错误: 未知交易所 {exchange_str}[/red]")
        sys.exit(1)

    if not quiet:
        console.print(f"[blue]下载 {symbol} {interval} 数据，范围: {start_dt.date()} 至 {end_dt.date()}...[/blue]")

    # 下载数据
    bars: List[BarData] = []
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console, disable=quiet) as progress:
        progress.add_task(description="下载中...", total=None)

        if source in ("vnpy", "auto"):
            bars = fetch_from_vnpy_datafeed(code, vnpy_exchange, vnpy_interval, start_dt, end_dt)
        if not bars and source in ("akshare", "auto"):
            if not quiet:
                console.print("[yellow]尝试从AKShare下载...[/yellow]")
            bars = fetch_from_akshare(code, exchange_str, interval, start_dt, end_dt)

    if not bars:
        if not quiet:
            console.print("[yellow]未获取到数据。[/yellow]")
        sys.exit(0)

    if not quiet:
        console.print(f"[green]成功下载 {len(bars)} 条K线[/green]")

    # 保存到数据库
    if save:
        db = get_database()
        ok = db.save_bar_data(bars)
        if not quiet:
            if ok:
                console.print(f"[green]已保存 {len(bars)} 条到数据库[/green]")
            else:
                console.print("[red]数据库保存失败[/red]")

    # 输出
    if output == "json":
        data = {
            "symbol": symbol,
            "interval": interval,
            "count": len(bars),
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
        click.echo(json.dumps(data, ensure_ascii=False, indent=2))
    elif output == "csv":
        import csv
        import io

        out = io.StringIO()
        writer = csv.writer(out)
        writer.writerow(["datetime", "symbol", "exchange", "open", "high", "low", "close", "volume", "turnover", "open_interest"])
        for b in bars:
            writer.writerow([
                b.datetime.isoformat(), b.symbol, b.exchange.value,
                b.open_price, b.high_price, b.low_price, b.close_price,
                b.volume, b.turnover, b.open_interest,
            ])
        click.echo(out.getvalue())


if __name__ == "__main__":
    main()

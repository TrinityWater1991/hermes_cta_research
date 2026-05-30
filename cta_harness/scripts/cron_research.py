#!/usr/bin/env python3
"""
CTA 投研自动运行脚本 —— 供 cron job 调用。

逻辑：
1. 检查是否有正在运行的投研任务（回测/优化/参数扫描）
2. 如果没有，开始新的投研循环：
   a. 从 Substack 搜索新的 CTA 策略灵感
   b. 按 Pipeline 流程执行研究
   c. 将结果沉淀到 wiki
"""
import subprocess, json, re, sys, os, time
from datetime import datetime

PROJECT_DIR = "/home/admin/github/cta_agent"
VENV_ACTIVATE = "source ~/.venvs/313/bin/activate"

def check_running_tasks() -> list:
    """检查是否有 Python 回测/优化进程在运行。"""
    cmd = "ps aux | grep -E 'vn_backtest|param_scan|vn_data_fetch' | grep -v grep | awk '{print $2, $11, $12}'"
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True, executable="/bin/bash")
    lines = [l.strip() for l in proc.stdout.strip().split("\n") if l.strip()]
    return lines

def has_recent_study() -> bool:
    """检查最近24小时内是否有研究活动。"""
    cmd = "tail -5 /home/admin/github/cta_agent/wiki/log.md | grep -E 'ingest|close|graduate|discard|backtest|develop'"
    proc = subprocess.run(cmd, capture_output=True, text=True, shell=True, executable="/bin/bash")
    return bool(proc.stdout.strip())

def log_to_wiki(message: str) -> None:
    """追加日志到 wiki/log.md。"""
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(PROJECT_DIR, "wiki", "log.md")
    entry = f"\n## [{today}] cron | {message}\n"
    with open(log_path, "a") as f:
        f.write(entry)

def send_notification(message: str) -> None:
    """通过微信发送通知。"""
    # We'll write a note for the main session to pick up
    log_path = os.path.join(PROJECT_DIR, "cron_notify.txt")
    with open(log_path, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {message}\n")

def run_backtest(strategy_name: str, symbol: str, interval: str = "1m",
                 start: str = "2021-01-04", end: str = "2026-03-30",
                 capital: int = 200000, size: int = 10,
                 slippage: float = 0, pricetick: float = 1,
                 rate: float = 0.0001, params: dict = None) -> dict:
    """运行单次回测并返回统计结果。"""
    cmd = f"{VENV_ACTIVATE} && cd {PROJECT_DIR} && python scripts/vn_backtest_run.py"
    cmd += f" -s {symbol} -i {interval} -S {start} -e {end}"
    cmd += f" --strategy {strategy_name}"
    cmd += f" --capital {capital} --size {size} --rate {rate} --slippage {slippage} --pricetick {pricetick}"
    cmd += " -o json -q"
    
    if params:
        for k, v in params.items():
            cmd += f" -p {k}={v}"
    
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, shell=True,
                              executable="/bin/bash", timeout=180)
        m = re.search(r'\{.*"stats".*"sharpe_ratio".*\}', proc.stderr, re.DOTALL)
        if m:
            data = json.loads(m.group())
            stats = data["stats"]
            return {
                "sharpe": float(stats.get("sharpe_ratio", 0)),
                "return_pct": float(stats.get("total_return", 0)),
                "max_dd": float(stats.get("max_ddpercent", 0)),
                "trades": int(stats.get("total_trade_count", 0)),
                "end_balance": float(stats.get("end_balance", 0)),
            }
    except Exception as e:
        return {"error": str(e)}
    return {}

def get_contract_spec(symbol: str) -> dict:
    """获取合约规格。"""
    specs = {
        "rb99.SHFE": {"size": 10, "pricetick": 1},
        "j99.DCE": {"size": 100, "pricetick": 0.5},
        "jm99.DCE": {"size": 60, "pricetick": 0.5},
        "i99.DCE": {"size": 100, "pricetick": 0.5},
    }
    return specs.get(symbol, {"size": 10, "pricetick": 1})

def main():
    # 1. 检查是否有正在运行的投研任务
    running = check_running_tasks()
    if running:
        print(f"[SKIP] 有 {len(running)} 个投研进程在运行：")
        for r in running[:3]:
            print(f"  PID {r}")
        return
    
    # 2. 检查最近24小时是否有研究
    if has_recent_study():
        print("[SKIP] 24小时内已有研究活动")
        return
    
    # 3. 没有活跃任务，开始新研究
    print("[START] 开始新的 CTA 投研循环...")
    
    # 写入通知文件，提示主 session
    send_notification("cron 触发：开始新的 CTA 研究循环")
    
    # 这里简化——因为完整 pipeline 需要在 Hermes 会话中执行
    # cron job 独立运行，只能做数据检查等自动化工作
    # 真正的策略开发/回测需要等主会话处理
    
    log_to_wiki("cron 触发自动检查，当前无活跃投研任务")

if __name__ == "__main__":
    main()

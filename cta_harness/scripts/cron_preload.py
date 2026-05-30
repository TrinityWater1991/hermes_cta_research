#!/usr/bin/env python3
"""Cron job 预加载脚本：输出 AGENTS.md 中的工程规范和关键规则。"""
import os

PROJECT_DIR = "/home/admin/github/cta_agent"
AGENTS_PATH = os.path.join(PROJECT_DIR, "AGENTS.md")

def extract_section(lines, start_marker, end_marker=None):
    """从 AGENTS.md 提取章节内容。"""
    capturing = False
    result = []
    for line in lines:
        if start_marker in line:
            capturing = True
            continue
        if capturing:
            if end_marker and end_marker in line:
                break
            result.append(line.rstrip())
    return [l for l in result if l.strip()]  # 去空行

try:
    with open(AGENTS_PATH) as f:
        content = f.read()
        lines = content.split("\n")
except Exception:
    print("<!-- 无法读取 AGENTS.md -->")
    raise

print("<!-- AGENTS.md 工程规范（由 cron_preload.py 注入）-->")

# 1. 工程规则
rules = extract_section(lines, "### 语言与沟通", "### Python 编码规范")
print("## 沟通规则")
for r in rules:
    if r.startswith("- "):
        print(r)

# 2. Python 规范
py_rules = extract_section(lines, "### Python 编码规范", "### 类型系统要求")
print("\n## Python 规范")
for r in py_rules:
    if r.startswith("- "):
        print(r)

# 3. 类型系统
type_rules = extract_section(lines, "### 类型系统要求", "### 质量检查")
print("\n## 类型要求")
for r in type_rules:
    if r.startswith("- "):
        print(r)

# 4. 修改原则
mod_rules = extract_section(lines, "### 修改原则", "### 任务执行与验证")
print("\n## 修改原则")
for r in mod_rules:
    if r.startswith("- "):
        print(r)

# 5. 任务验证
task_rules = extract_section(lines, "### 任务执行与验证", "### 命名与可读性")
print("\n## 任务验证")
for r in task_rules:
    if r.startswith("- "):
        print(r)

# 6. 命名规则
name_rules = extract_section(lines, "### 命名与可读性", "---")
print("\n## 命名与可读性")
for r in name_rules:
    if r.startswith("- "):
        print(r)

# 7. 策略代码规范
print("\n## 策略代码规范")
code_lines = extract_section(lines, "## 策略代码规范", "## 回测配置")
for r in code_lines:
    print(r)

# 8. 命名规范表
print("\n## 命名规范")
in_table = False
for line in lines:
    if "| 策略代码 |" in line:
        in_table = True
    if in_table:
        if line.startswith("##"):
            break
        if line.startswith("|"):
            print(line)

# 9. 策略毕业标准
print("\n## 毕业标准")
grad_lines = extract_section(lines, "## 策略毕业标准", "## 命名规范")
for r in grad_lines:
    if r.startswith("- "):
        print(r)

# 10. Pipeline 默认回测参数
print("\n## 默认回测参数")
in_params = False
for line in lines:
    if "### 默认回测参数" in line:
        in_params = True
        continue
    if in_params:
        if line.startswith("```") and "capital" in line or line.strip() == "```":
            in_table = not in_table if '```' in line else in_table
            continue
        if "合约: " in line or "数据周期: " in line or "capital: " in line or line.strip().startswith("- "):
            print(line.strip())
        if line.startswith("### "):
            break

print("<!-- END AGENTS.md 规范 -->")

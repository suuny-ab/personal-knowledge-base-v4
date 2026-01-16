#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 状态摘要脚本
生成详细的 Git 仓库状态报告
"""

import subprocess
import sys
from datetime import datetime

def run_command(cmd):
    """执行 Git 命令并返回输出"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return str(e), 1

def print_section(title, content=""):
    """打印带标题的章节"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    if content:
        print(content)

def main():
    """主函数"""
    print(f"\n📊 Git 仓库状态报告")
    print(f"⏰ 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 1. 当前分支
    stdout, _ = run_command("git branch --show-current")
    print_section("📍 当前分支", stdout)

    # 2. 远程仓库
    stdout, _ = run_command("git remote -v")
    print_section("🌐 远程仓库", stdout if stdout else "无")

    # 3. 工作区状态
    stdout, _ = run_command("git status --short")
    if stdout:
        print_section("📝 工作区状态")
        lines = stdout.split('\n')
        for line in lines:
            status = line[:2].strip()
            file = line[3:]
            status_map = {
                'M': '已修改',
                'A': '已添加',
                'D': '已删除',
                'R': '已重命名',
                '??': '未跟踪',
                '!!': '已忽略'
            }
            status_desc = status_map.get(status, status)
            print(f"  [{status_desc}] {file}")
    else:
        print_section("📝 工作区状态", "✅ 工作区干净")

    # 4. 最近提交
    stdout, _ = run_command("git log --oneline -5 --graph --decorate")
    if stdout:
        print_section("📜 最近 5 次提交")
        print(stdout)

    # 5. 分支列表
    stdout, _ = run_command("git branch -v")
    if stdout:
        print_section("🌿 本地分支")
        print(stdout)

    # 6. 储存列表
    stdout, _ = run_command("git stash list")
    if stdout:
        print_section("📦 储存列表", stdout)

    # 7. 未推送的提交
    stdout, _ = run_command("git log --oneline @{u}..HEAD 2>/dev/null")
    if stdout:
        print_section("⬆️  未推送的提交", stdout)

    print(f"\n{'='*60}")
    print("✅ 报告生成完成")
    print('='*60 + "\n")

if __name__ == "__main__":
    main()

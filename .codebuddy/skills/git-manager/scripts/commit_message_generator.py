#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Git 提交消息生成器
基于代码变更自动生成符合规范的提交消息
"""

import subprocess
import sys
from typing import List, Tuple, Dict

def run_command(cmd: str) -> Tuple[str, int]:
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

def get_staged_files() -> List[str]:
    """获取已暂存的文件列表"""
    stdout, _ = run_command("git diff --cached --name-only")
    if not stdout:
        return []
    return stdout.split('\n')

def get_file_changes(filename: str) -> Dict[str, int]:
    """分析文件的变更统计"""
    stdout, _ = run_command(f"git diff --cached --numstat {filename}")
    if not stdout:
        return {'additions': 0, 'deletions': 0}
    parts = stdout.split()
    return {
        'additions': int(parts[0]) if parts[0] != '-' else 0,
        'deletions': int(parts[1]) if parts[1] != '-' else 0
    }

def analyze_changes(files: List[str]) -> Dict[str, any]:
    """分析所有变更"""
    analysis = {
        'total_files': len(files),
        'additions': 0,
        'deletions': 0,
        'file_types': {},
        'directories': {},
        'features': [],
        'fixes': [],
        'docs': [],
        'refactors': [],
        'others': []
    }

    for file in files:
        # 统计变更
        changes = get_file_changes(file)
        analysis['additions'] += changes['additions']
        analysis['deletions'] += changes['deletions']

        # 分析文件类型
        ext = file.split('.')[-1] if '.' in file else 'no_ext'
        analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1

        # 分析目录
        dir_name = '/'.join(file.split('/')[:-1]) if '/' in file else 'root'
        analysis['directories'][dir_name] = analysis['directories'].get(dir_name, 0) + 1

        # 根据文件名和路径推断变更类型
        file_lower = file.lower()
        if any(keyword in file_lower for keyword in ['test', 'spec']):
            analysis['features'].append(('test', file))
        elif any(keyword in file_lower for keyword in ['readme', 'doc', 'docs']):
            analysis['docs'].append(file)
        elif any(keyword in file_lower for keyword in ['fix', 'bug', 'patch']):
            analysis['fixes'].append(file)
        elif any(keyword in file_lower for keyword in ['refactor', 'cleanup']):
            analysis['refactors'].append(file)
        else:
            analysis['features'].append(('feat', file))

    return analysis

def determine_commit_type(analysis: Dict[str, any]) -> str:
    """确定提交类型"""
    counts = {
        'fix': len(analysis['fixes']),
        'test': sum(1 for t, f in analysis['features'] if t == 'test'),
        'docs': len(analysis['docs']),
        'refactor': len(analysis['refactors']),
        'feat': sum(1 for t, f in analysis['features'] if t == 'feat')
    }

    if counts['fix'] > 0:
        return 'fix'
    elif counts['test'] > 0 and counts['feat'] == 0:
        return 'test'
    elif counts['docs'] > 0 and sum(counts.values()) == counts['docs']:
        return 'docs'
    elif counts['refactor'] > 0 and sum(counts.values()) == counts['refactor']:
        return 'refactor'
    else:
        return 'feat'

def determine_scope(analysis: Dict[str, any]) -> str:
    """确定提交范围"""
    # 基于目录推断范围
    if len(analysis['directories']) == 1:
        dir_name = list(analysis['directories'].keys())[0]
        return dir_name.split('/')[-1]

    # 基于文件类型推断
    if len(analysis['file_types']) == 1:
        file_type = list(analysis['file_types'].keys())[0]
        return file_type

    return 'global'

def generate_summary(analysis: Dict[str, any], commit_type: str, scope: str) -> str:
    """生成提交摘要"""
    type_names = {
        'feat': '新功能',
        'fix': '修复',
        'docs': '文档',
        'style': '格式',
        'refactor': '重构',
        'test': '测试',
        'chore': '维护'
    }

    summary_type = type_names.get(commit_type, '更新')

    if commit_type == 'feat':
        return f"{summary_type}: 添加{determine_features(analysis)}"
    elif commit_type == 'fix':
        return f"{summary_type}: 修复{determine_issues(analysis)}"
    elif commit_type == 'docs':
        return f"{summary_type}: 更新文档"
    elif commit_type == 'test':
        return f"{summary_type}: 添加测试"
    else:
        return f"{summary_type}: 通用更新"

def determine_features(analysis: Dict[str, any]) -> str:
    """推断功能描述"""
    files = [f for t, f in analysis['features'] if t == 'feat']
    if not files:
        return "功能"

    # 从文件名中提取关键词
    keywords = []
    for file in files:
        name = file.split('/')[-1].split('.')[0]
        if len(name) > 2:
            keywords.append(name)

    if keywords:
        return f" {keywords[0]} 相关功能"
    return "功能"

def determine_issues(analysis: Dict[str, any]) -> str:
    """推断问题描述"""
    if analysis['fixes']:
        return f" {analysis['fixes'][0]} 相关问题"
    return "问题"

def generate_description(analysis: Dict[str, any]) -> str:
    """生成详细描述"""
    lines = []

    # 统计信息
    if analysis['total_files'] > 1:
        lines.append(f"- 修改 {analysis['total_files']} 个文件")

    # 变更统计
    if analysis['additions'] > 0 or analysis['deletions'] > 0:
        additions = f"+{analysis['additions']}"
        deletions = f"-{analysis['deletions']}"
        lines.append(f"- 变更: {additions} {deletions}")

    # 文件列表
    if analysis['total_files'] <= 5:
        files = get_staged_files()
        for file in files:
            lines.append(f"- {file}")

    return '\n'.join(lines) if lines else "- 代码更新"

def generate_commit_message() -> str:
    """生成完整的提交消息"""
    # 获取已暂存的文件
    files = get_staged_files()

    if not files:
        print("❌ 没有已暂存的文件")
        print("提示: 使用 'git add <file>' 暂存文件")
        sys.exit(1)

    # 分析变更
    analysis = analyze_changes(files)

    # 确定类型和范围
    commit_type = determine_commit_type(analysis)
    scope = determine_scope(analysis)

    # 生成消息
    summary = generate_summary(analysis, commit_type, scope)
    description = generate_description(analysis)

    # 组装完整消息
    message = f"{commit_type}({scope}): {summary}\n\n{description}"

    return message

def print_section(title: str, content: str = ""):
    """打印带标题的章节"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)
    if content:
        print(content)

def main():
    """主函数"""
    print("\n📝 Git 提交消息生成器")
    print("="*60)

    # 检查是否在 Git 仓库中
    _, rc = run_command("git rev-parse --git-dir")
    if rc != 0:
        print("❌ 当前目录不是 Git 仓库")
        sys.exit(1)

    # 生成提交消息
    message = generate_commit_message()

    # 显示生成的消息
    print_section("✅ 生成的提交消息")
    print(message)

    # 显示详细信息
    files = get_staged_files()
    print_section("📋 已暂存的文件", '\n'.join(f"  • {f}" for f in files))

    # 提示
    print_section("💡 提示")
    print("  使用以下命令提交:")
    print(f"  git commit -m \"{message}\"")
    print("\n  或手动编辑后提交:")
    print("  git commit")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()

# Git 常用命令参考

## 基础操作

### 配置
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
git config --global init.defaultBranch main
```

### 初始化
```bash
git init                    # 初始化仓库
git clone <url>            # 克隆远程仓库
```

### 状态查看
```bash
git status                 # 查看工作区状态
git log                    # 查看提交历史
git log --oneline          # 简洁的提交历史
git log --graph            # 图形化显示历史
git diff                   # 查看未暂存的变更
git diff --staged          # 查看已暂存的变更
```

## 分支管理

### 创建与切换
```bash
git branch <branch-name>              # 创建分支
git checkout <branch-name>            # 切换分支
git checkout -b <branch-name>         # 创建并切换分支
git switch <branch-name>              # 切换分支（新语法）
git switch -c <branch-name>           # 创建并切换分支（新语法）
```

### 查看
```bash
git branch                   # 列出本地分支
git branch -r                # 列出远程分支
git branch -a                # 列出所有分支
git branch -v                # 显示分支详细信息
```

### 删除
```bash
git branch -d <branch-name>  # 删除已合并分支
git branch -D <branch-name>  # 强制删除分支
```

## 提交管理

### 暂存与提交
```bash
git add <file>               # 暂存文件
git add .                    # 暂存所有变更
git add -A                   # 暂存所有变更（包括删除）
git commit -m "message"      # 提交变更
git commit -am "message"     # 暂存并提交已跟踪文件
```

### 修改提交
```bash
git commit --amend           # 修改最后一次提交
git commit --amend -m "new message"  # 修改提交信息
```

## 撤销操作

### 工作区撤销
```bash
git restore <file>           # 恢复文件到最近提交状态
git checkout -- <file>       # 旧语法，功能相同
```

### 暂存区撤销
```bash
git restore --staged <file>  # 取消暂存
git reset HEAD <file>        # 旧语法，功能相同
```

### 提交撤销
```bash
git reset --soft HEAD~1      # 撤销提交，保留变更在暂存区
git reset --mixed HEAD~1     # 撤销提交，保留变更在工作区
git reset --hard HEAD~1      # 撤销提交，丢弃所有变更
```

### Revert（推荐用于已推送的提交）
```bash
git revert <commit-hash>     # 创建新提交撤销指定提交
```

## 合并与变基

### 合并
```bash
git merge <branch>          # 合并分支
git merge --no-ff <branch>  # 禁用快进合并，保留分支历史
```

### 变基
```bash
git rebase <branch>         # 变基到指定分支
git rebase -i HEAD~3         # 交互式变基最近3个提交
```

## 远程操作

### 远程仓库管理
```bash
git remote -v                # 查看远程仓库
git remote add origin <url> # 添加远程仓库
git remote remove origin    # 删除远程仓库
git remote set-url origin <url>  # 修改远程仓库URL
```

### 推送与拉取
```bash
git push                    # 推送到远程
git push -u origin main     # 推送并设置上游分支
git push origin <branch>    # 推送指定分支
git push --force            # 强制推送（谨慎使用）
git pull                    # 拉取并合并
git pull --rebase           # 拉取并变基
git fetch                   # 获取远程变更但不合并
```

## 标签管理

```bash
git tag                     # 列出标签
git tag <tag-name>          # 创建标签
git tag -a <tag-name> -m "message"  # 创建带注释的标签
git tag -d <tag-name>       # 删除标签
git push origin <tag-name>  # 推送标签
git push --tags             # 推送所有标签
```

## 储存（Stash）

```bash
git stash                   # 储存当前工作
git stash save "message"    # 带消息的储存
git stash list              # 列出储存
git stash show              # 显示储存内容
git stash pop               # 恢复并删除储存
git stash apply             # 恢复但不删除储存
git stash drop              # 删除储存
git stash clear             # 清空所有储存
```

## 其他实用命令

### 查看变更统计
```bash
git log --stat              # 显示每次提交的变更统计
git shortlog                # 按作者分组显示提交
```

### 查看文件历史
```bash
git log <file>              # 查看文件历史
git blame <file>            # 显示每行是谁修改的
```

### 搜索
```bash
git log --grep="keyword"    # 搜索提交信息
git log --author="name"     # 按作者搜索
```

### 清理
```bash
git clean -fd               # 删除未跟踪的文件和目录
git gc                      # 垃圾回收，优化仓库
```

## 高级操作

### Cherry-pick
```bash
git cherry-pick <commit-hash>  # 挑选指定提交应用到当前分支
```

### Bisect（二分查找）
```bash
git bisect start            # 开始二分查找
git bisect bad              # 标记当前提交为有问题
git bisect good <commit>    # 标记指定提交为好的
git bisect reset            # 重置二分查找
```

### Submodule
```bash
git submodule add <url>     # 添加子模块
git submodule update --init --recursive  # 初始化和更新子模块
```

# Git 常见问题排查

## 常见错误及解决方案

### 1. "fatal: not a git repository"

**原因：** 当前目录不是 Git 仓库

**解决：**
```bash
# 初始化仓库
git init

# 或切换到正确的仓库目录
cd path/to/repository
```

---

### 2. "error: pathspec 'xxx' did not match any file(s) known to git"

**原因：** 文件未被跟踪或路径错误

**解决：**
```bash
# 检查文件状态
git status

# 添加文件到跟踪
git add <file>

# 或检查文件路径是否正确
```

---

### 3. "fatal: refusing to merge unrelated histories"

**原因：** 两个仓库没有共同祖先

**解决：**
```bash
# 允许合并不相关的历史
git pull origin main --allow-unrelated-histories
```

---

### 4. "CONFLICT (content): Merge conflict in xxx"

**原因：** 合并时产生冲突

**解决：**
```bash
# 1. 查看冲突文件
git status

# 2. 手动编辑文件，解决冲突
# 标记：
<<<<<<< HEAD
你的变更
=======
别人的变更
>>>>>>> branch-name

# 3. 标记冲突已解决
git add <file>

# 4. 完成合并
git commit
```

---

## 性能问题

### 仓库操作缓慢

**原因：** 仓库历史庞大或大文件过多

**解决：**
```bash
# 清理无用对象
git gc

# 清理引用
git prune
```

---

## 回滚问题

### 想要撤销某个提交但不知道用哪个命令

**决策树：**
```
是否已推送？
├─ 是
│   └─ 使用 git revert（创建新提交撤销）
└─ 否
    └─ 是否保留变更？
        ├─ 是 → git reset --soft
        └─ 否 → git reset --hard
```

---

## 获取帮助

```bash
# 查看命令帮助
git <command> --help

# 查看完整文档
man git
```

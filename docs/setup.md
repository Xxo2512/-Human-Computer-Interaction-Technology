# 开发环境搭建与 GitHub 协作指南

> 这份文档给组里每位新加入的成员用。按步骤照做即可。

---

## Part 1 · 第一次拉代码和配环境

### 1. 安装前置工具

- **Git**:<https://git-scm.com/download/win>
- **Python 3.10 或 3.11 或 3.12**:<https://www.python.org/downloads/>
  - 安装时勾选 "Add Python to PATH"
- (可选)**VS Code**:<https://code.visualstudio.com/>,装 Python、Jupyter 扩展

打开终端验证:

```bash
git --version       # 应显示 git version 2.x
python --version    # 应显示 Python 3.10+
```

### 2. 配置 Git 身份(只做一次)

```bash
git config --global user.name  "你的名字"
git config --global user.email "你的GitHub邮箱"
```

### 3. 克隆仓库

```bash
cd 你想放项目的目录
git clone https://github.com/<组长账号>/Human-Computer-Interaction-Technology.git
cd Human-Computer-Interaction-Technology
```

### 4. 创建虚拟环境并安装依赖

```bash
# 创建 venv
python -m venv .venv

# 激活(Windows Git Bash)
source .venv/Scripts/activate

# 激活(Windows PowerShell)
.venv\Scripts\Activate.ps1

# 激活(macOS/Linux)
source .venv/bin/activate

# 升级 pip(用清华镜像加速)
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装依赖
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 5. 验证环境

```bash
python -c "import mne, sklearn, numpy, scipy, pandas, yaml; print('环境 OK, mne=', mne.__version__)"
```

出现 `环境 OK, mne= 1.x.x` 就算成功。

### 6. VS Code 选择解释器

`Ctrl+Shift+P` → `Python: Select Interpreter` → 选 `.venv/Scripts/python.exe`。
之后打开终端(`Ctrl+`` ` ``)会自动激活 venv。

---

## Part 2 · 日常协作流程

### 标准流程(强烈建议每个人都按这个走)

```bash
# 1. 拉取最新 dev
git checkout dev
git pull origin dev

# 2. 从 dev 开分支(名字按模板)
git checkout -b feat/p3-psd-features

# 3. 写代码 & 本地测试
# ... 修改文件 ...

# 4. 提交
git add src/features/extract.py
git commit -m "feat(features): 添加 Welch PSD 计算与 5 频带切分"

# 5. 推送
git push -u origin feat/p3-psd-features

# 6. 在 GitHub 网页发起 Pull Request
#    base: dev   <--   compare: feat/p3-psd-features
#    @ 另一个组员 review

# 7. review 通过后,在 GitHub 点 Merge
# 8. 本地删掉分支
git checkout dev
git pull
git branch -d feat/p3-psd-features
```

### 分支命名规范

- `feat/p{编号}-{功能}`:新功能,如 `feat/p1-ica`
- `fix/{描述}`:修 bug,如 `fix/baseline-window`
- `docs/{描述}`:只改文档

### 提交信息规范

```
<type>(<scope>): <短描述>

type: feat(新功能) / fix(修bug) / docs(文档) / refactor(重构) / test(测试) / chore(杂)
scope: preprocess / features / models / transfer / utils / docs
```

好例子:
- ✅ `feat(preprocess): 带通滤波 4-45Hz + 50Hz 陷波`
- ✅ `fix(features): 修正 FAA 左右脑电极顺序`

坏例子:
- ❌ `update`(不知道改了什么)
- ❌ `修改代码`(同上)

---

## Part 3 · 组长首次推送到 GitHub

> 这一节只给组长做一次。

1. 在 GitHub 网页 `New repository`
   - 名称:`Human-Computer-Interaction-Technology`
   - **不要**勾选 "Initialize with README"(本地已经有了)
   - 可选 Private
2. 复制仓库地址(SSH 或 HTTPS,推荐 HTTPS)
3. 在项目根目录执行:

```bash
git remote add origin https://github.com/<你的账号>/Human-Computer-Interaction-Technology.git
git push -u origin main

# 创建 dev 分支并推送
git checkout -b dev
git push -u origin dev
```

4. 在 GitHub 仓库 `Settings → Branches → Add rule`:
   - 保护 `main`:require PR review,禁止直接 push
5. `Settings → Collaborators` 邀请其他 5 个组员

---

## Part 4 · 常见问题

### Q: `pip install` 很慢 / 超时

用国内镜像(清华):
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
或永久设置:
```bash
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: 我想把数据放进 git?

**不要**。DEAP 数据超过 1GB 且有授权限制。数据只放本地 `data/raw/`,已在 `.gitignore` 里屏蔽。

### Q: 不小心把数据提交了怎么办?

```bash
git rm -r --cached data/raw
git commit -m "chore: untrack data/raw"
```

### Q: 我本地的修改和别人冲突了

```bash
git pull --rebase origin dev
# 手动解决冲突后
git add <冲突文件>
git rebase --continue
```

### Q: PowerShell 激活 venv 报脚本执行策略错误

以管理员打开 PowerShell 执行一次:
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

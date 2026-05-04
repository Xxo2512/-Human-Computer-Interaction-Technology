# EEG 情感识别与迁移学习(DEAP)

人机交互课程大作业 · 6 人小组项目

## 项目目标

基于 DEAP 数据集,完成 EEG 信号的预处理、情感三分类(积极/中性/消极)、跨被试迁移学习对比实验,并给出交互应用展望。

## 技术栈

- Python 3.10+
- MNE-Python(脑电预处理)
- scikit-learn(分类与评估)
- NumPy / SciPy / pandas / matplotlib / seaborn
- PyYAML(配置管理)

## 目录结构

```
.
├── configs/              # 全局配置(阈值、频带、路径)
├── data/
│   ├── raw/              # DEAP 原始 .bdf 或 .dat (不进 git)
│   ├── preproc/          # P1 输出: *_clean_raw.fif
│   └── epochs/           # P2 输出: *_epo.fif + labels.csv
├── features/             # P3 输出: *_features.npz
├── models/               # P4/P5 输出: *.pkl + metrics.json
├── src/
│   ├── preprocess/       # P1 + P2: 预处理 / 分段 / 基线
│   ├── features/         # P3: 时域 + 频域特征
│   ├── models/           # P4: 被试内三分类基线
│   ├── transfer/         # P5: 跨被试迁移学习
│   └── utils/            # 公共 I/O、配置、日志
├── notebooks/            # 探索性 notebook(非正式代码)
├── reports/
│   └── figs/             # 所有图表统一放这里
├── tests/                # 单元测试(可选)
├── requirements.txt
├── .gitignore
└── README.md
```

## 环境搭建

```bash
# 1. 克隆仓库
git clone <仓库地址>
cd Human-Computer-Interaction-Technology

# 2. 创建虚拟环境
python -m venv .venv

# 3. 激活虚拟环境
# Windows (Git Bash):
source .venv/Scripts/activate
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# macOS / Linux:
source .venv/bin/activate

# 4. 升级 pip 并安装依赖
python -m pip install --upgrade pip
pip install -r requirements.txt

# 5. 验证
python -c "import mne, sklearn, numpy, scipy, pandas; print('OK')"
```

## 数据准备

本项目**使用 DEAP 原始 `.bdf` 版本**,自己完成完整预处理流程,以满足任务 1
对滤波/去伪迹/分段/基线校正的展示要求。

数据不提交到仓库(`.gitignore` 已屏蔽)。下载后放置:

```
data/raw/
├── s01.bdf
├── s02.bdf
├── ...
└── s32.bdf          # 来自 Kaggle 或 DEAP 官方
```

**第一步:数据结构探测**(任何人拿到数据先跑这个,确认通道名/采样率/事件码):

```bash
python scripts/inspect_bdf.py data/raw/s01.bdf
```

根据输出结果,P1 需要更新 `configs/config.yaml` 中的 `eog_channels` 和
`event_id_video_start` 字段。

## 分支策略

- `main`:稳定分支,受保护,只接受 Pull Request
- `dev`:集成分支,每周合并一次到 main
- 个人分支命名:`feat/p{编号}-{功能}`,例如 `feat/p1-preprocess`、`feat/p3-features`

工作流:

```bash
git checkout dev
git pull
git checkout -b feat/p1-preprocess
# ... 开发 & 提交 ...
git push -u origin feat/p1-preprocess
# 在 GitHub 发起 PR: feat/p1-preprocess -> dev
```

## 提交信息规范

```
<type>(<scope>): <短描述>

type: feat / fix / docs / refactor / test / chore
scope: preprocess / features / models / transfer / utils / docs
```

示例:
- `feat(preprocess): 完成带通滤波与 ICA 去伪迹`
- `fix(features): 修正 FAA 对数底数错误`

## 分工(详见 docs/team-plan.md)

| 成员 | 任务 | 交付 |
|------|------|------|
| P1 | 预处理:导入/滤波/去伪迹 | `src/preprocess/filter_ica.py` |
| P2 | 分段/基线/标签 | `src/preprocess/epoching.py` |
| P3 | 时域+频域特征 | `src/features/extract.py` |
| P4 | 被试内三分类基线 | `src/models/train_within.py` |
| P5 | 跨被试迁移学习 | `src/transfer/train_cross.py` |
| P6 | 结果分析+展望+统稿 | `reports/` + 汇总脚本 |

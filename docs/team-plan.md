# 六人分工详表

## 目录产物约定

| 角色 | 代码位置 | 输出到 |
|------|---------|--------|
| P1 预处理 | `src/preprocess/filter_ica.py` | `data/preproc/sXX_clean_raw.fif` |
| P2 分段/标签 | `src/preprocess/epoching.py` | `data/epochs/sXX_epo.fif` + `data/epochs/labels.csv` |
| P3 特征 | `src/features/extract.py` | `features/sXX_features.npz` (X, y, feat_names) |
| P4 基线建模 | `src/models/train_within.py` | `models/within_{model}.pkl` + `models/within_metrics.json` |
| P5 迁移学习 | `src/transfer/train_cross.py` | `models/transfer_{method}.pkl` + `models/transfer_metrics.json` |
| P6 汇总 | `src/utils/report.py` | `reports/figs/*.png` + 报告正文 |

## 接口约定(谁先动谁后动)

> 本项目使用 **DEAP 原始 `.bdf` 版本**,P1 负责完整预处理,P2 负责分段。

1. **P0 · 数据探测(所有人第一步)**:拿到数据后跑 `python scripts/inspect_bdf.py data/raw/s01.bdf`,把输出贴到群里。P1 据此更新 `config.yaml` 里的 `eog_channels` 和 `event_id_video_start`。
2. **P1 → P2**:P1 对每个 `.bdf` 执行 resample(512→256)→ 带通(1–50Hz)→ notch(50Hz)→ 平均参考 → ICA 去眼电肌电,产出 `sXX_clean_raw.fif`(`mne.io.Raw`,256Hz,32 EEG 通道)
3. **P2 → P3**:P2 用 `mne.find_events` 从 Status 通道解出 40 段视频的起始点,按 tmin=-3 / tmax=60 切 epoch,做基线校正,产出 `sXX_epo.fif` + `labels.csv`(trial_id, subject, valence_raw, arousal_raw, label_3class)
4. **P3 → P4/P5**:`sXX_features.npz` 固定含三个字段
   - `X`: shape `(n_trials, n_features)` float32
   - `y`: shape `(n_trials,)` int64,0=negative / 1=neutral / 2=positive
   - `feat_names`: shape `(n_features,)` str

任何人想改接口,先在群里通知,改完更新本文件。

## 每周同步

- 每周固定一次 30min 会议,进度 + 卡点
- PR 必须 ≥ 1 人 review 才能 merge 到 `dev`
- 每周五把 `dev` 合到 `main`,打 tag `vW1`, `vW2`, `vW3`

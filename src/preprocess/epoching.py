import pickle
import numpy as np
import mne
import pandas as pd

# ========== 配置参数 ==========
SFREQ = 128
CHANNEL_NAMES = [f"EEG{i:02d}" for i in range(1, 33)]
ALL_SUBJECTS = [f"s{i:02d}" for i in range(1, 33)]  # 自动生成s01到s32

all_epochs_list = []
all_labels_list = []

# ========== 批量处理所有被试 ==========
for SUBJECT_ID in ALL_SUBJECTS:
    print(f"正在处理 {SUBJECT_ID}...")
    
    # 1. 加载单个被试数据
    with open(f'data/data_preprocessed_python/{SUBJECT_ID}.dat', 'rb') as f:
        data = pickle.load(f, encoding='latin1')
    eeg_data = data['data'][:, :32, :]
    labels = data['labels']
    
    info = mne.create_info(ch_names=CHANNEL_NAMES, sfreq=SFREQ, ch_types='eeg')
    
    for video_idx in range(40):
        # 2. 分段
        raw = mne.io.RawArray(eeg_data[video_idx], info)
        events = mne.make_fixed_length_events(raw, duration=1.0)
        epochs = mne.Epochs(raw, events, tmin=0, tmax=1.0 - 1/SFREQ, baseline=None, preload=True, verbose=False)
        
        # 3. 基线校正
        baseline_data = epochs[:3].get_data()
        baseline_mean = np.mean(baseline_data, axis=(0, 2), keepdims=True)
        experiment_epochs = epochs[3:]
        experiment_data = experiment_epochs.get_data() - baseline_mean
        experiment_epochs._data = experiment_data
        
        all_epochs_list.append(experiment_epochs)
        
        # 4. 生成标签
        valence = labels[video_idx, 0]
        label = 0 if valence < 4 else (1 if valence <= 6 else 2)
        all_labels_list.extend([(video_idx, SUBJECT_ID, valence, label)] * len(experiment_epochs))

# ========== 合并所有被试的结果 ==========
print("正在合并所有被试数据...")
combined_epochs = mne.concatenate_epochs(all_epochs_list)

# ========== 保存结果 ==========
combined_epochs.save('data/epochs/all_subjects_epo.fif', overwrite=True)
labels_df = pd.DataFrame(all_labels_list, columns=['trial_id', 'subject', 'valence_raw', 'label_3class'])
labels_df.to_csv('data/epochs/labels.csv', index=False)

print(f"✅ 全部处理完成！共处理32个被试，生成 {len(combined_epochs)} 个epoch")
print("文件已保存到 data/epochs/ 文件夹：")
print("  - all_subjects_epo.fif（所有被试的分段数据）")
print("  - labels.csv（所有被试的标签）")
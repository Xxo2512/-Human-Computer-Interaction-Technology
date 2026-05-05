import pickle
import numpy as np
import mne
import pandas as pd

# ========== 配置参数 ==========
SFREQ = 128
CHANNEL_NAMES = [f"EEG{i:02d}" for i in range(1, 33)]
ALL_SUBJECTS = [f"s{i:02d}" for i in range(1, 33)]  # 32个被试s01~s32

all_labels_list = []

# ========== 逐个处理每个被试，单独保存 ==========
for SUBJECT_ID in ALL_SUBJECTS:
    print(f"正在处理 {SUBJECT_ID}...")
    
    # 读取原始dat文件
    with open(f'data/data_preprocessed_python/{SUBJECT_ID}.dat', 'rb') as f:
        data = pickle.load(f, encoding='latin1')
    eeg_data = data['data'][:, :32, :]
    labels = data['labels']
    
    # 创建mne格式信息
    info = mne.create_info(ch_names=CHANNEL_NAMES, sfreq=SFREQ, ch_types='eeg')
    subject_epochs = []
    
    # 处理每个视频trial
    for video_idx in range(40):
        raw = mne.io.RawArray(eeg_data[video_idx], info)
        # 按1秒分段
        events = mne.make_fixed_length_events(raw, duration=1.0)
        epochs = mne.Epochs(raw, events, tmin=0, tmax=1.0 - 1/SFREQ, baseline=None, preload=True, verbose=False)
        
        # 基线校正（用前3秒基线）
        baseline_data = epochs[:3].get_data()
        baseline_mean = np.mean(baseline_data, axis=(0, 2), keepdims=True)
        experiment_epochs = epochs[3:]
        experiment_epochs._data = experiment_epochs.get_data() - baseline_mean
        
        subject_epochs.append(experiment_epochs)
        
        # 记录标签
        valence = labels[video_idx, 0]
        label = 0 if valence < 4 else (1 if valence <= 6 else 2)
        all_labels_list.extend([(video_idx, SUBJECT_ID, valence, label)] * len(experiment_epochs))
    
    # 单独保存当前被试的fif文件
    combined = mne.concatenate_epochs(subject_epochs)
    combined.save(f'data/epochs/{SUBJECT_ID}_epo.fif', overwrite=True)
    print(f"✅ {SUBJECT_ID} 保存完成")

# 保存总标签文件
labels_df = pd.DataFrame(all_labels_list, columns=['trial_id', 'subject', 'valence_raw', 'label_3class'])
labels_df.to_csv('data/epochs/labels.csv', index=False)
print("🎉 全部32个被试处理完成！")
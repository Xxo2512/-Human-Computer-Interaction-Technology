"""探测 DEAP 原始 .bdf 数据的真实结构。

用法:
    python scripts/inspect_bdf.py data/raw/s01.bdf

输出通道名、采样率、时长、事件码分布 —— P1 据此确认 config.yaml 里的
eog_channels / event_id 是否正确。
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import mne
import numpy as np


def inspect(bdf_path: Path) -> None:
    print(f"\n===== {bdf_path.name} =====")
    raw = mne.io.read_raw_bdf(bdf_path, preload=False, verbose="ERROR")

    info = raw.info
    print(f"采样率        : {info['sfreq']} Hz")
    print(f"通道总数      : {len(info['ch_names'])}")
    print(f"录制时长      : {raw.n_times / info['sfreq']:.1f} s "
          f"({raw.n_times / info['sfreq'] / 60:.1f} min)")
    print(f"通道类型分布  : {Counter(info.get_channel_types())}")

    print("\n前 40 个通道名:")
    for i, ch in enumerate(info["ch_names"][:40]):
        print(f"  [{i:2d}] {ch}")

    status_candidates = [c for c in info["ch_names"] if "status" in c.lower() or "stim" in c.lower()]
    print(f"\nStatus/Stim 通道: {status_candidates}")

    if status_candidates:
        stim_ch = status_candidates[0]
        try:
            events = mne.find_events(
                raw, stim_channel=stim_ch, shortest_event=1, verbose="ERROR"
            )
            print(f"事件总数      : {len(events)}")
            if len(events):
                codes = Counter(events[:, 2].tolist())
                print(f"事件码分布    : {dict(sorted(codes.items()))}")
                print("  (DEAP 官方: 1=exp start, 2=sync, 3=fixation,")
                print("              4=music, 5=video start, 7=video end, 8=exp end)")
        except Exception as e:
            print(f"读取事件失败  : {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python scripts/inspect_bdf.py <bdf_path> [bdf_path2 ...]")
        sys.exit(1)
    for p in sys.argv[1:]:
        inspect(Path(p))

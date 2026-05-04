"""P1: data import, bandpass, and artifact removal (ICA + muscle annotations)."""
from __future__ import annotations

import argparse
from pathlib import Path

import mne
from mne.preprocessing import ICA, annotate_muscle_zscore

from src.utils.io import load_config, resolve_path


DEAP_CHANNELS = [
    "Fp1",
    "AF3",
    "F3",
    "F7",
    "FC5",
    "FC1",
    "C3",
    "T7",
    "CP5",
    "CP1",
    "P3",
    "P7",
    "PO3",
    "O1",
    "Oz",
    "Pz",
    "Fp2",
    "AF4",
    "F4",
    "F8",
    "FC6",
    "FC2",
    "C4",
    "T8",
    "CP6",
    "CP2",
    "P4",
    "P8",
    "PO4",
    "O2",
    "hEOG",
    "vEOG",
    "zEMG",
    "tEMG",
    "GSR",
    "Resp",
    "Plet",
    "Temp",
]


def _set_channel_types(raw: mne.io.BaseRaw) -> None:
    type_map = {
        "hEOG": "eog",
        "vEOG": "eog",
        "zEMG": "emg",
        "tEMG": "emg",
        "GSR": "misc",
        "Resp": "misc",
        "Plet": "misc",
        "Temp": "misc",
    }
    present = {name: kind for name, kind in type_map.items() if name in raw.ch_names}
    if present:
        raw.set_channel_types(present)


def load_raw_bdf(bdf_path: Path) -> mne.io.Raw:
    raw = mne.io.read_raw_bdf(bdf_path, preload=True)
    _set_channel_types(raw)
    if len(raw.ch_names) == len(DEAP_CHANNELS):
        raw.rename_channels({old: new for old, new in zip(raw.ch_names, DEAP_CHANNELS)})
        _set_channel_types(raw)
    raw.set_montage("standard_1020", on_missing="ignore")
    return raw


def apply_bandpass(raw: mne.io.Raw, l_freq: float, h_freq: float, notch_freq: float) -> None:
    raw.notch_filter(notch_freq, picks="eeg")
    raw.filter(l_freq=l_freq, h_freq=h_freq, picks="eeg", fir_design="firwin")
    raw.set_eeg_reference("average", projection=False)


def remove_artifacts(raw: mne.io.Raw, cfg: dict) -> tuple[mne.io.Raw, ICA]:
    # Mark high muscle activity so ICA ignores those segments during fit.
    annot, _ = annotate_muscle_zscore(raw, ch_type="eeg", threshold=4.0)
    raw.set_annotations(raw.annotations + annot)

    ica_cfg = cfg["preprocess"]["ica"]
    ica = ICA(
        n_components=ica_cfg["n_components"],
        random_state=ica_cfg["random_state"],
        method=ica_cfg["method"],
    )
    ica.fit(raw, picks="eeg", reject_by_annotation=True)

    eog_channels = ica_cfg.get("eog_channels", [])
    bads: set[int] = set()
    for ch_name in eog_channels:
        if ch_name in raw.ch_names:
            eog_inds, _ = ica.find_bads_eog(raw, ch_name=ch_name)
            bads.update(eog_inds)
    ica.exclude = sorted(bads)

    cleaned = ica.apply(raw.copy())
    return cleaned, ica


def preprocess_subject(subject_id: str, cfg: dict) -> Path:
    raw_root = resolve_path(cfg["paths"]["data_raw"]) / "data_original"
    bdf_path = raw_root / f"{subject_id}.bdf"
    if not bdf_path.exists():
        raise FileNotFoundError(f"Missing file: {bdf_path}")

    raw = load_raw_bdf(bdf_path)
    bp = cfg["preprocess"]["bandpass"]
    apply_bandpass(raw, bp["l_freq"], bp["h_freq"], cfg["preprocess"]["notch_freq"])
    cleaned, _ = remove_artifacts(raw, cfg)

    out_dir = resolve_path(cfg["paths"]["data_preproc"])
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{subject_id}_clean_raw.fif"
    cleaned.save(out_path, overwrite=True)
    return out_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DEAP preprocess: import, bandpass, ICA.")
    parser.add_argument("--subject", required=True, help="Subject id like s01")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    cfg = load_config()
    out_path = preprocess_subject(args.subject, cfg)
    print(f"Saved: {out_path}")


if __name__ == "__main__":
    main()

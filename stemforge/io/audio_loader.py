"""Audio loading with a sane sample-rate contract.

Everything upstream of the backends sees float32, channels-last, at
the backend's declared sample rate. This module is the only place
that touches soundfile / librosa directly.
"""

from __future__ import annotations

from pathlib import Path

import librosa
import numpy as np
import soundfile as sf

SUPPORTED_EXTS = {".wav", ".flac", ".mp3", ".ogg", ".m4a", ".aiff"}


def load_audio(path: Path, target_sr: int | None = None) -> tuple[np.ndarray, int]:
    if path.suffix.lower() not in SUPPORTED_EXTS:
        raise ValueError(f"unsupported audio extension: {path.suffix}")
    if path.suffix.lower() == ".mp3":
        # soundfile can't decode mp3 on all builds; route through librosa.
        y, sr = librosa.load(str(path), sr=target_sr, mono=False)
        return _to_channels_last(y), sr
    data, sr = sf.read(str(path), always_2d=True, dtype="float32")
    if target_sr is not None and sr != target_sr:
        data = librosa.resample(data.T, orig_sr=sr, target_sr=target_sr).T
        sr = target_sr
    return data.astype(np.float32, copy=False), sr


def _to_channels_last(y: np.ndarray) -> np.ndarray:
    if y.ndim == 1:
        return np.stack([y, y], axis=1).astype(np.float32)
    return y.T.astype(np.float32)
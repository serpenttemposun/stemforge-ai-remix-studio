"""Stem writer — encodes float32 arrays to wav/flac/mp3 on disk.

MP3 goes through ffmpeg if present; otherwise we refuse rather than
silently emit a wav with an .mp3 extension.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf


def write_stem(
    dest: Path,
    arr: np.ndarray,
    sr: int,
    out_format: str = "wav",
    bitrate: int = 320,
) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if out_format in ("wav", "flac"):
        subtype = "PCM_16" if out_format == "wav" else "PCM_24"
        sf.write(str(dest), arr, sr, subtype=subtype)
        return
    if out_format == "mp3":
        if shutil.which("ffmpeg") is None:
            raise RuntimeError("ffmpeg required for mp3 export; install and retry")
        tmp_wav = dest.with_suffix(".tmp.wav")
        sf.write(str(tmp_wav), arr, sr, subtype="PCM_16")
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-i", str(tmp_wav),
             "-b:a", f"{bitrate}k", str(dest)],
            check=True,
        )
        tmp_wav.unlink(missing_ok=True)
        return
    raise ValueError(f"unsupported output format: {out_format}")
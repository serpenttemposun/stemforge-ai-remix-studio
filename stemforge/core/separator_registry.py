"""Runtime registry that maps friendly stem names to backend outputs.

Backends don't all emit the same stem vocabulary — Demucs ships
vocals/drums/bass/other, some MDX models ship vocals/instrumental only.
This module normalizes that so the render pipeline can ask for "bass"
and get silence-filled output if the backend doesn't produce it.
"""

from __future__ import annotations

import numpy as np

CANONICAL_STEMS = ("vocals", "drums", "bass", "other", "piano", "guitar")

_ALIASES: dict[str, str] = {
    "instrumental": "other",
    "accompaniment": "other",
    "no_vocals": "other",
    "vox": "vocals",
    "voice": "vocals",
    "kick": "drums",
    "percussion": "drums",
}


def canonicalize(name: str) -> str:
    key = name.strip().lower().replace("-", "_")
    return _ALIASES.get(key, key)


def normalize(stems: dict[str, np.ndarray], sr: int, n_samples: int) -> dict[str, np.ndarray]:
    """Alias-map stems and fill missing canonical stems with silence."""
    out: dict[str, np.ndarray] = {}
    for raw_name, arr in stems.items():
        out[canonicalize(raw_name)] = arr
    for name in CANONICAL_STEMS:
        if name not in out:
            out[name] = np.zeros((n_samples, 2), dtype=np.float32)
    return out
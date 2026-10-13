"""Remix handler — recombines separated stems through a preset.

A remix preset is a small declarative spec (gain per stem, mute flags,
optional time-warp and crossfade) applied to a StemSet. Presets are
JSON; they are never eval'd.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from stemforge.core.separator_base import StemSet


@dataclass(slots=True)
class RemixPreset:
    name: str
    gains: dict[str, float]
    mutes: set[str]
    crossfade_ms: int = 0
    time_warp: float = 1.0

    @classmethod
    def from_json(cls, path: Path) -> "RemixPreset":
        raw = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            name=raw.get("name", path.stem),
            gains={str(k): float(v) for k, v in raw.get("gains", {}).items()},
            mutes=set(raw.get("mutes", [])),
            crossfade_ms=int(raw.get("crossfade_ms", 0)),
            time_warp=float(raw.get("time_warp", 1.0)),
        )


class RemixHandler:
    def __init__(self, preset: RemixPreset) -> None:
        self._preset = preset

    def apply(self, stems: StemSet) -> np.ndarray:
        length = max((a.shape[0] for a in stems.stems.values()), default=0)
        channels = max((a.shape[1] for a in stems.stems.values()), default=2)
        bus = np.zeros((length, channels), dtype=np.float32)
        for name, arr in stems.stems.items():
            if name in self._preset.mutes:
                continue
            gain = self._preset.gains.get(name, 1.0)
            padded = _pad_to(arr, length, channels)
            bus += padded * gain
        peak = float(np.max(np.abs(bus))) or 1.0
        if peak > 1.0:
            bus /= peak
        return bus


def _pad_to(arr: np.ndarray, length: int, channels: int) -> np.ndarray:
    out = np.zeros((length, channels), dtype=np.float32)
    n, c = arr.shape
    out[:n, :c] = arr
    return out
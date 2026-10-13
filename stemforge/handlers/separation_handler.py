"""Separation handler — drives a single split job from disk to disk."""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

from stemforge.core.engine import StemForgeEngine
from stemforge.core.separator_registry import normalize
from stemforge.io.audio_loader import load_audio
from stemforge.io.stem_writer import write_stem
from stemforge.utils.timing import Stopwatch

log = logging.getLogger(__name__)


class SeparationHandler:
    def __init__(self, engine: StemForgeEngine) -> None:
        self._engine = engine

    def run(
        self,
        mix_path: Path,
        out_dir: Path,
        stems: list[str],
        out_format: str = "wav",
        bitrate: int = 320,
    ) -> dict[str, Path]:
        sw = Stopwatch()
        mix, sr = load_audio(mix_path)
        log.info("loaded %s  sr=%d  shape=%s in %.2fs", mix_path.name, sr, mix.shape, sw.lap())

        result = self._engine.separate(mix, sr)
        n_samples = mix.shape[0]
        normalized = normalize(result.stems, sr, n_samples)

        written: dict[str, Path] = {}
        out_dir.mkdir(parents=True, exist_ok=True)
        base = mix_path.stem
        for stem in stems:
            if stem not in normalized:
                log.warning("backend produced no stem %r, skipping", stem)
                continue
            arr = np.clip(normalized[stem], -1.0, 1.0)
            dest = out_dir / f"{base}__{stem}.{out_format}"
            write_stem(dest, arr, sr, out_format=out_format, bitrate=bitrate)
            written[stem] = dest
        log.info("wrote %d stems in %.2fs", len(written), sw.lap())
        return written
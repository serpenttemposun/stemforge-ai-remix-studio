"""Demucs (htdemucs) backend adapter.

Wraps a Demucs-style 4-stem model. In production this shells out to the
`demucs` package; here we keep the interface stable and lazy-import so
the rest of StemForge works without Demucs installed.
"""

from __future__ import annotations

import logging

import numpy as np

log = logging.getLogger(__name__)


class DemucsBackend:
    name = "demucs"
    sample_rate = 44100
    STEMS = ("vocals", "drums", "bass", "other")

    def __init__(self, device: str = "auto", model: str = "htdemucs") -> None:
        self.device = device
        self.model_name = model
        self._model = None

    def load(self) -> None:
        try:
            import demucs.api  # type: ignore[import-not-found]
        except ImportError as exc:  # pragma: no cover - optional dep
            raise RuntimeError("demucs not installed; pip install demucs") from exc
        self._model = demucs.api.Separator(model=self.model_name, device=self.device)
        log.info("demucs model %s ready on %s", self.model_name, self.device)

    def separate(self, mix: np.ndarray, sr: int) -> dict[str, np.ndarray]:
        if self._model is None:
            raise RuntimeError("call load() before separate()")
        if sr != self.sample_rate:
            raise ValueError(f"demucs expects {self.sample_rate} Hz, got {sr}")
        _, out = self._model.separate_tensor(mix.T)  # type: ignore[union-attr]
        return {name: arr.T.astype(np.float32) for name, arr in out.items()}

    def unload(self) -> None:
        self._model = None
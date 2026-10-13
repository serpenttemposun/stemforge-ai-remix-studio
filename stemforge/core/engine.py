"""StemForgeEngine — backend registry and separation orchestration.

The engine owns the lifecycle of exactly one active backend at a time.
Switching backends unloads the previous one to keep VRAM from
fragmenting across model swaps.
"""

from __future__ import annotations

import logging
from typing import Any

import numpy as np

from stemforge.core.separator_base import StemSeparator, StemSet

log = logging.getLogger(__name__)

BACKENDS: dict[str, str] = {
    "demucs": "stemforge.backends.demucs_backend:DemucsBackend",
    "mdx": "stemforge.backends.mdx_backend:MdxBackend",
    "spleeter": "stemforge.backends.spleeter_backend:SpleeterBackend",
    "onnx-custom": "stemforge.backends.onnx_backend:OnnxBackend",
}


def _resolve(dotted: str) -> Any:
    module_path, _, attr = dotted.partition(":")
    import importlib

    module = importlib.import_module(module_path)
    return getattr(module, attr)


class StemForgeEngine:
    def __init__(self, backend_name: str, backend: StemSeparator, device: str = "auto") -> None:
        self.backend_name = backend_name
        self._backend = backend
        self.device = device
        self._loaded = False

    @classmethod
    def from_config(cls, cfg: Any, device: str = "auto") -> "StemForgeEngine":
        backend_name = cfg.default_backend
        if backend_name not in BACKENDS:
            raise ValueError(f"unknown backend {backend_name!r}; known: {sorted(BACKENDS)}")
        backend_cls = _resolve(BACKENDS[backend_name])
        backend = backend_cls(device=device, **cfg.backend_kwargs.get(backend_name, {}))
        return cls(backend_name, backend, device=device)

    def load(self) -> None:
        if not self._loaded:
            log.info("loading backend %s on %s", self.backend_name, self.device)
            self._backend.load()
            self._loaded = True

    def separate(self, mix: np.ndarray, sr: int) -> StemSet:
        if not self._loaded:
            self.load()
        if mix.ndim not in (1, 2):
            raise ValueError(f"expected 1D or 2D mix, got shape {mix.shape}")
        stems = self._backend.separate(mix, sr)
        return StemSet(stems=stems, sample_rate=sr)

    def switch(self, backend_name: str, **kwargs: Any) -> None:
        if backend_name == self.backend_name:
            return
        self._backend.unload()
        backend_cls = _resolve(BACKENDS[backend_name])
        self._backend = backend_cls(device=self.device, **kwargs)
        self.backend_name = backend_name
        self._loaded = False

    def close(self) -> None:
        self._backend.unload()
        self._loaded = False
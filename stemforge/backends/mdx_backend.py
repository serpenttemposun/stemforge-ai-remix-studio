"""MDX-Net backend adapter.

MDX-Net checkpoints are typically 2-stem (vocals/instrumental). We
promote the instrumental to "other" so the registry sees a full set.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)


class MdxBackend:
    name = "mdx"
    sample_rate = 44100

    def __init__(self, device: str = "auto", checkpoint: str | None = None) -> None:
        self.device = device
        self.checkpoint = Path(checkpoint) if checkpoint else None
        self._session = None

    def load(self) -> None:
        import onnxruntime as ort

        if self.checkpoint is None or not self.checkpoint.exists():
            raise FileNotFoundError(f"mdx checkpoint not found: {self.checkpoint}")
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"] if self.device != "cpu" else ["CPUExecutionProvider"]
        self._session = ort.InferenceSession(str(self.checkpoint), providers=providers)

    def separate(self, mix: np.ndarray, sr: int) -> dict[str, np.ndarray]:
        if self._session is None:
            raise RuntimeError("call load() before separate()")
        # Placeholder for the real STFT -> model -> iSTFT path.
        vocals = mix * 0.0
        instrumental = mix.copy()
        return {"vocals": vocals, "instrumental": instrumental}

    def unload(self) -> None:
        self._session = None
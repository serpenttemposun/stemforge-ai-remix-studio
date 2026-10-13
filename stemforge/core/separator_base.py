"""StemSeparator protocol and StemSet container.

Every backend implements StemSeparator. The engine only ever talks to
this interface, which keeps backend code swappable and testable without
loading real weights.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

import numpy as np


@dataclass(slots=True)
class StemSet:
    """A dict of stem name -> mono/stereo float32 array at `sample_rate`.

    Arrays are channels-last: shape (n_samples, channels). Values are
    nominally in [-1.0, 1.0]; backends may exceed slightly and callers
    should clamp before writing.
    """

    stems: dict[str, np.ndarray] = field(default_factory=dict)
    sample_rate: int = 44100

    def __getitem__(self, name: str) -> np.ndarray:
        return self.stems[name]

    def __iter__(self):
        return iter(self.stems)

    def __len__(self) -> int:
        return len(self.stems)

    def names(self) -> list[str]:
        return list(self.stems.keys())


@runtime_checkable
class StemSeparator(Protocol):
    """Backend contract.

    Lifecycle: `load()` once, `separate()` many times, `unload()` on
    teardown. `separate` must be safe to call from a worker thread; a
    backend that isn't thread-safe should guard internally.
    """

    name: str
    sample_rate: int

    def load(self) -> None:
        """Load weights into memory. May download on first run."""
        ...

    def separate(self, mix: np.ndarray, sr: int) -> dict[str, np.ndarray]:
        """Split a mix into named stems. Raises ValueError on bad shape."""
        ...

    def unload(self) -> None:
        """Release weights and device memory."""
        ...
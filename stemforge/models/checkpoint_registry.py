"""Checkpoint registry — knows where weights live and how to verify them.

We never ship weights in the repo. This registry describes known
checkpoints (name, URL, sha256, size) and resolves them against the
local cache directory.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from platformdirs import user_cache_dir

CACHE_ROOT = Path(user_cache_dir("stemforge")) / "checkpoints"


@dataclass(frozen=True, slots=True)
class CheckpointSpec:
    name: str
    filename: str
    sha256: str
    url: str
    size_bytes: int


KNOWN: dict[str, CheckpointSpec] = {
    "htdemucs": CheckpointSpec(
        name="htdemucs",
        filename="htdemucs.onnx",
        sha256="0000000000000000000000000000000000000000000000000000000000000000",
        url="https://example.invalid/stemforge/htdemucs.onnx",
        size_bytes=0,
    ),
    "mdx_extra": CheckpointSpec(
        name="mdx_extra",
        filename="mdx_extra.onnx",
        sha256="0000000000000000000000000000000000000000000000000000000000000000",
        url="https://example.invalid/stemforge/mdx_extra.onnx",
        size_bytes=0,
    ),
}


def resolve(name: str)
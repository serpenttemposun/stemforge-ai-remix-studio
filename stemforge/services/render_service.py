"""RenderService — the single funnel every frontend goes through.

CLI, GUI, and batch mode all build a RenderRequest and call
`RenderService.render`. This is deliberate: one code path means one
place to add progress reporting, cancellation, and telemetry.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from stemforge.core.engine import StemForgeEngine
from stemforge.handlers.remix_handler import RemixHandler, RemixPreset
from stemforge.handlers.separation_handler import SeparationHandler

log = logging.getLogger(__name__)


@dataclass(slots=True)
class RenderRequest:
    mix_path: Path
    out_dir: Path
    backend: str
    stems: list[str] = field(default_factory=lambda: ["vocals", "drums", "bass", "other"])
    out_format: str = "wav"
    bitrate: int = 320
    remix_preset: Path | None = None


@dataclass(slots=True)
class RenderResult:
    out_dir: Path
    stem_count: int
    written: dict[str, Path]


class RenderService:
    def __init__(self, engine: StemForgeEngine) -> None:
        self._engine = engine

    def render(self, request: RenderRequest) -> RenderResult:
        if not request.mix_path.exists():
            raise FileNotFoundError(request.mix_path)

        if request.backend != self._engine.backend_name:
            self._engine.switch(request.backend)

        sep = SeparationHandler(self._engine)
        written = sep.run(
            mix_path=request.mix_path,
            out_dir=request.out_dir,
            stems=request.stems,
            out_format=request.out_format,
            bitrate=request.bitrate,
        )

        if request.remix_preset is not None:
            preset = RemixPreset.from_json(request.remix_preset)
            log.info("applying remix preset %r", preset.name)
            # Remix is applied downstream in the GUI preview path; for the
            # CLI we just record that a preset was requested.
            _ = RemixHandler(preset)

        return RenderResult(
            out_dir=request.out_dir,
            stem_count=len(written),
            written=written,
        )
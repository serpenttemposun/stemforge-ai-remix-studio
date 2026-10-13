"""CLI entrypoint for StemForge.

Wires config -> engine -> render pipeline -> disk. This is the module
invoked by the `stemforge` console script. Keep it thin: parse args,
build an engine, hand off to the render service.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from rich.console import Console

from stemforge.config.loader import load_config
from stemforge.core.engine import StemForgeEngine
from stemforge.services.render_service import RenderService, RenderRequest
from stemforge.utils.logging import configure_logging

console = Console()


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="stemforge",
        description="AI remix / stem separation generator — split a track into stems.",
    )
    p.add_argument("mix", type=Path, help="Path to the input mix (wav/flac/mp3).")
    p.add_argument("-o", "--out", type=Path, default=Path("output"), help="Output directory.")
    p.add_argument(
        "--backend",
        default=None,
        help="Separation backend: demucs / mdx / spleeter / onnx-custom.",
    )
    p.add_argument(
        "--stems",
        default="vocals,drums,bass,other",
        help="Comma-separated stems to render.",
    )
    p.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda", "dml"])
    p.add_argument("--bitrate", type=int, default=320, help="MP3 bitrate if encoding mp3.")
    p.add_argument("--format", default="wav", choices=["wav", "flac", "mp3"])
    p.add_argument("--remix", type=Path, default=None, help="Optional remix preset to apply.")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    configure_logging(verbose=args.verbose)

    cfg = load_config()
    engine = StemForgeEngine.from_config(cfg, device=args.device)

    request = RenderRequest(
        mix_path=args.mix.resolve(),
        out_dir=args.out.resolve(),
        backend=args.backend or cfg.default_backend,
        stems=[s.strip() for s in args.stems.split(",") if s.strip()],
        out_format=args.format,
        bitrate=args.bitrate,
        remix_preset=args.remix,
    )

    service = RenderService(engine)
    try:
        result = service.render(request)
    except FileNotFoundError as exc:
        console.print(f"[red]missing input:[/red] {exc}")
        return 2
    except Exception as exc:  # noqa: BLE001 — CLI boundary, report and exit
        console.print(f"[red]render failed:[/red] {exc}")
        return 1

    console.print(f"[green]done[/green] → {result.out_dir}  ({result.stem_count} stems)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
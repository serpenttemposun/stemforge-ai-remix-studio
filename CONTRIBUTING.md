# Contributing to stemforge-ai-remix-studio

Thanks for wanting to hack on StemForge. This is a hobbyist/educational
desktop tool for AI-driven stem separation and remixing. PRs welcome.

## Ground rules

- Python 3.11+ is the target runtime. CI runs 3.11 and 3.12 on Windows
  and Linux. macOS is best-effort.
- Keep the separation backends pluggable. If you add a new model
  (Demucs variant, MDX-Net, Spleeter fork, custom ONNX), implement the
  `StemSeparator` protocol in `stemforge/core/separator_base.py` and
  register it in `stemforge/core/engine.py`.
- Don't commit model weights. Ever. `.gitignore` already blocks the
  common extensions. If you need a test fixture, use a tiny stub ONNX
  and drop it in `tests/fixtures/`.
- Audio I/O changes go through `stemforge/io/audio_loader.py`. Don't
  sprinkle `soundfile.read` calls across handlers.

## Dev setup

```
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
```

For GPU acceleration install the CUDA extras:

```
pip install -e ".[cuda]"
```

## Branching

- `main` is release. Don't push to it directly.
- `dev` is integration.
- Feature branches: `feat/<short-name>`, fixes: `fix/<short-name>`.

## Code style

- `ruff` + `black`, line length 100.
- Type hints on all public functions. `mypy --strict` on `stemforge/core/`.
- No bare `except:`. If you're swallowing an exception, log it with
  context and re-raise unless it's a known recoverable audio decode
  failure.

## Adding a separation backend

1. Subclass `StemSeparator` in `stemforge/core/separator_base.py`.
2. Implement `load()`, `separate(mix, sr) -> dict[str, np.ndarray]`,
   and `unload()`.
3. Register in `stemforge/core/engine.py` `BACKENDS` dict.
4. Add a config block in `stemforge/config/defaults.toml`.
5. Add a test in `tests/test_separator_registry.py`.

## Reporting bugs

Include: OS, Python version, backend name, sample rate, number of
stems requested, and the full traceback. Attach a 5-second clip if
you can — audio bugs are impossible to reproduce without audio.

## License

By contributing you agree your work is released under the MIT license.
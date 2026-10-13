# Security Policy — stemforge-ai-remix-studio

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.6.x   | yes       |
| 0.5.x   | security fixes only |
| < 0.5   | no        |

## Reporting a vulnerability

Open a private security advisory on GitHub, or email
`security@stemforge.local` (PGP key in `docs/pgp.txt` when we publish
one). Please don't open a public issue for anything exploitable.

Expected response: 72 hours to acknowledge, 7 days to triage.

## Threat model — what actually matters here

StemForge is a **local desktop tool**. It reads audio files, runs
neural separation, and writes stems. The interesting attack surface:

1. **Model file loading.** We load ONNX / PyTorch checkpoints from
   `models/checkpoints/`. Pickle-based `.pt` files are arbitrary code
   execution vectors. We only ship `.onnx` and `.safetensors` in the
   default download path for exactly this reason. If you add a `.pt`
   loader, treat it as untrusted input and sandbox it.
2. **Audio decoder parsers.** `libsndfile`, `ffmpeg`, and `audioread`
   have historically had memory-safety bugs on malformed containers.
   We call them as subprocesses where possible and never feed a
   user-supplied path directly into a shell.
3. **Plugin / preset loading.** `.sfpreset` files are JSON. We do
   NOT `eval` them. If you see `eval` or `exec` anywhere in a PR
   touching presets, that's a hard reject.
4. **Cloud inference opt-in.** When `[cloud] enabled = true`, stems
   and mix excerpts leave the machine. This is off by default. Never
   flip it silently.
5. **Path traversal in batch mode.** Batch separation walks a user
   directory. Output paths are joined with `Path.resolve()` and
   checked against the output root before writing.

## What is explicitly out of scope

- Denial of service via giant audio files (that's a feature request,
  not a vuln — use the streaming loader).
- Local privilege escalation on a machine where the attacker already
  runs code as you.
- Anything requiring the user to feed the tool a checkpoint they
  downloaded from a sketchy source. Verify your checksums.

## Disclosure

We'll credit reporters in the release notes unless you ask us not to.
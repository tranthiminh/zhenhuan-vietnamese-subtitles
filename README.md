# Zhen Huan Vietnamese Subtitles

Cloud-first workflow for producing careful Vietnamese subtitles from Mandarin audio, with special support for **Empresses in the Palace / 后宫·甄嬛传** terminology.

> This repository contains tooling and translation resources only. It does **not** include copyrighted source video/audio or full episode subtitles.

## Goals

1. Transcribe Mandarin accurately with Gemini 3.5 Transcribe.
2. Preserve character names, palace names, Qing harem ranks, and forms of address consistently.
3. Produce Vietnamese `.srt` subtitles with readable segmentation and timing.
4. Make the workflow reproducible and shareable through GitHub Actions.

## Why two transcription passes?

Gemini 3.5 Transcribe currently does not allow `custom_vocabulary` together with word-level timestamps. This project therefore uses:

- **Accuracy pass**: Chinese language hint + custom vocabulary, no word timestamps.
- **Timing pass**: word-level timestamps, no custom vocabulary.
- **Alignment + translation pass**: a Gemini general model receives both outputs plus the glossary and produces Vietnamese SRT.

## Repository layout

```text
.github/workflows/
  subtitle_pipeline.yml
scripts/
  transcribe.py
  translate_to_vi.py
  validate_srt.py
  merge_srt.py
  srt_utils.py
glossary/
  characters.csv
  ranks.csv
  places.csv
  forms_of_address.csv
docs/
  STYLE_GUIDE.vi.md
  CLOUD_WORKFLOW.vi.md
examples/
  sample.env
output/
  .gitkeep
```

## Quick start with GitHub Actions

1. Create a public or private GitHub repository from this project.
2. Open **Settings → Secrets and variables → Actions**.
3. Add a repository secret named `GEMINI_API_KEY`.
4. Open **Actions → Build Vietnamese subtitles → Run workflow**.
5. Enter a direct URL to an audio/video **file** you are legally allowed to process, plus an episode ID such as `EP03`.
6. The workflow normalizes the media, automatically splits long episodes into 20-minute chunks, transcribes each chunk twice, translates them, validates them and merges them into one final SRT.
7. Download the generated artifact when the workflow finishes.

### Important privacy note

A `workflow_dispatch` text input is not appropriate for a secret/private signed URL in a public repository. For private media, use a private repository or run the scripts locally/Colab instead.

## Local run for a short clip

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:GEMINI_API_KEY="YOUR_KEY"

python scripts/transcribe.py clip.wav --episode EP03.part000 --out-dir output
python scripts/translate_to_vi.py `
  --accuracy output/EP03.part000.zh.accuracy.txt `
  --timed output/EP03.part000.zh.timed.txt `
  --out output/EP03.part000.vi.srt
python scripts/validate_srt.py output/EP03.part000.vi.srt
```

For full-length episodes, the recommended path is GitHub Actions because the workflow automatically normalizes and chunks the media.

## Translation philosophy

This project does not translate subtitle lines independently. It uses episode-level context and locked terminology so that titles such as `答应`, `常在`, `贵人`, `嫔`, `妃`, `贵妃`, `皇贵妃`, and `皇后` remain consistent throughout the series.

## Status

Early public scaffold. The next improvements should focus on scene-aware segmentation, human review tools, and a terminology consistency report.

## License

Code and original documentation: MIT License. Glossary entries are factual terminology mappings and may be expanded by contributors.

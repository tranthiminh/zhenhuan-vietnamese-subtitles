#!/usr/bin/env python3
import argparse
import csv
import os
from pathlib import Path

from google import genai


def load_vocab(glossary_dir: Path) -> list[str]:
    terms: list[str] = []
    for path in sorted(glossary_dir.glob("*.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as f:
            for row in csv.DictReader(f):
                zh = (row.get("zh") or "").strip()
                if zh and zh not in terms:
                    terms.append(zh)
    return terms[:100]


def run_pass(client, audio_file, config):
    interaction = client.interactions.create(
        model="gemini-3.5-transcribe",
        input=[
            {
                "type": "audio",
                "uri": audio_file.uri,
                "mime_type": audio_file.mime_type,
            }
        ],
        generation_config={"transcription_config": config},
    )
    return interaction.output_text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("audio")
    parser.add_argument("--episode", required=True)
    parser.add_argument("--out-dir", default="output")
    parser.add_argument("--glossary-dir", default="glossary")
    args = parser.parse_args()

    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("Missing GEMINI_API_KEY environment variable")

    audio_path = Path(args.audio)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    glossary_dir = Path(args.glossary_dir)

    client = genai.Client()
    uploaded = client.files.upload(file=str(audio_path))

    vocab = load_vocab(glossary_dir)
    accuracy_text = run_pass(
        client,
        uploaded,
        {
            "language_codes": ["zh-CN"],
            "custom_vocabulary": vocab,
        },
    )
    (out_dir / f"{args.episode}.zh.accuracy.txt").write_text(
        accuracy_text, encoding="utf-8"
    )

    timed_text = run_pass(
        client,
        uploaded,
        {
            "language_codes": ["zh-CN"],
            "mode": {
                "type": "verbatim",
                "timestamp_granularities": ["word"],
            },
        },
    )
    (out_dir / f"{args.episode}.zh.timed.txt").write_text(
        timed_text, encoding="utf-8"
    )

    print(f"Created transcription outputs in {out_dir}")


if __name__ == "__main__":
    main()

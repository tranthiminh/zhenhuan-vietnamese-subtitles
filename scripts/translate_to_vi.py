#!/usr/bin/env python3
import argparse
import os
from pathlib import Path

from google import genai


def read_glossary_bundle(path: Path) -> str:
    chunks = []
    for file in sorted(path.glob("*.csv")):
        chunks.append(f"\n### {file.name}\n{file.read_text(encoding='utf-8-sig')}")
    return "\n".join(chunks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--accuracy", required=True)
    parser.add_argument("--timed", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--glossary-dir", default="glossary")
    parser.add_argument("--style-guide", default="docs/STYLE_GUIDE.vi.md")
    parser.add_argument(
        "--model",
        default=os.getenv("GEMINI_TRANSLATION_MODEL", "gemini-3.8-flash"),
    )
    args = parser.parse_args()

    if not os.getenv("GEMINI_API_KEY"):
        raise SystemExit("Missing GEMINI_API_KEY environment variable")

    accuracy = Path(args.accuracy).read_text(encoding="utf-8")
    timed = Path(args.timed).read_text(encoding="utf-8")
    glossary = read_glossary_bundle(Path(args.glossary_dir))
    style = Path(args.style_guide).read_text(encoding="utf-8")

    prompt = f"""
You are a professional Chinese-to-Vietnamese subtitle editor.
Create a Vietnamese SRT file from two transcriptions of the SAME audio.

RULES:
1. The ACCURACY transcript is the authority for Chinese wording, names and terminology.
2. The TIMED transcript is the authority for timing information.
3. Do not invent dialogue.
4. Follow the glossary exactly unless context proves an entry does not apply.
5. Follow the Vietnamese style guide.
6. Output ONLY valid SRT. No Markdown fences and no explanation.
7. Keep cues readable, normally at most 2 lines.
8. Preserve chronological order and avoid overlapping cues.

VIETNAMESE STYLE GUIDE:
{style}

GLOSSARY:
{glossary}

ACCURACY TRANSCRIPT:
{accuracy}

TIMED TRANSCRIPT:
{timed}
"""

    client = genai.Client()
    response = client.models.generate_content(model=args.model, contents=prompt)
    text = (response.text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.lower().startswith("srt"):
            text = text[3:].lstrip()

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(text.rstrip() + "\n", encoding="utf-8")
    print(f"Created {args.out}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import re
from pathlib import Path

from srt_utils import parse_srt, render_srt

PART_RE = re.compile(r"\.part(\d+)\.vi\.srt$")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="output")
    parser.add_argument("--episode", required=True)
    parser.add_argument("--chunk-seconds", type=int, default=1200)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    files = sorted(input_dir.glob(f"{args.episode}.part*.vi.srt"))
    if not files:
        raise SystemExit("No part SRT files found")

    merged = []
    for path in files:
        match = PART_RE.search(path.name)
        if not match:
            continue
        part_index = int(match.group(1))
        offset_ms = part_index * args.chunk_seconds * 1000
        cues = parse_srt(path.read_text(encoding="utf-8-sig"))
        for cue in cues:
            merged.append(
                {
                    "start_ms": cue["start_ms"] + offset_ms,
                    "end_ms": cue["end_ms"] + offset_ms,
                    "text": cue["text"],
                }
            )

    merged.sort(key=lambda c: (c["start_ms"], c["end_ms"]))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(render_srt(merged), encoding="utf-8")
    print(f"Merged {len(files)} parts into {args.out} ({len(merged)} cues)")


if __name__ == "__main__":
    main()

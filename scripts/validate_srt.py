#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

from srt_utils import parse_srt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("srt")
    args = parser.parse_args()

    try:
        cues = parse_srt(Path(args.srt).read_text(encoding="utf-8-sig"))
    except Exception as exc:
        print(f"SRT validation failed: {exc}")
        sys.exit(1)

    errors = []
    previous_end = -1
    for i, cue in enumerate(cues, start=1):
        start = cue["start_ms"]
        end = cue["end_ms"]
        text = cue["text"]
        if end <= start:
            errors.append(f"Cue {i}: end time is not after start time")
        if start < previous_end:
            errors.append(f"Cue {i}: overlaps previous cue")
        if not text:
            errors.append(f"Cue {i}: empty text")
        if len(text.splitlines()) > 2:
            errors.append(f"Cue {i}: more than 2 text lines")
        previous_end = max(previous_end, end)

    if errors:
        print("SRT validation failed:")
        for error in errors:
            print("-", error)
        sys.exit(1)

    print(f"SRT OK: {len(cues)} cues")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import re

TIMECODE_RE = re.compile(
    r"^(\d{2}):(\d{2}):(\d{2}),(\d{3})\s+-->\s+"
    r"(\d{2}):(\d{2}):(\d{2}),(\d{3})$"
)


def parse_timecode(value: str) -> int:
    h, m, s_ms = value.split(":")
    s, ms = s_ms.split(",")
    return (((int(h) * 60) + int(m)) * 60 + int(s)) * 1000 + int(ms)


def format_timecode(ms: int) -> str:
    if ms < 0:
        ms = 0
    h, rem = divmod(ms, 3_600_000)
    m, rem = divmod(rem, 60_000)
    s, milli = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{milli:03d}"


def parse_srt(text: str):
    normalized = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not normalized:
        return []
    blocks = re.split(r"\n{2,}", normalized)
    cues = []
    for block in blocks:
        lines = block.splitlines()
        if len(lines) < 3:
            raise ValueError(f"Invalid SRT block: {block!r}")
        try:
            int(lines[0].strip())
        except ValueError as exc:
            raise ValueError(f"Invalid SRT index: {lines[0]!r}") from exc
        match = TIMECODE_RE.match(lines[1].strip())
        if not match:
            raise ValueError(f"Invalid SRT timecode: {lines[1]!r}")
        left, right = [x.strip() for x in lines[1].split("-->", 1)]
        cues.append(
            {
                "start_ms": parse_timecode(left),
                "end_ms": parse_timecode(right),
                "text": "\n".join(lines[2:]).strip(),
            }
        )
    return cues


def render_srt(cues) -> str:
    blocks = []
    for idx, cue in enumerate(cues, start=1):
        blocks.append(
            f"{idx}\n"
            f"{format_timecode(cue['start_ms'])} --> {format_timecode(cue['end_ms'])}\n"
            f"{cue['text'].strip()}"
        )
    return "\n\n".join(blocks) + "\n"

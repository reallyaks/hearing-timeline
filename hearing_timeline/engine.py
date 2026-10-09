"""Rule extraction for a timestamped hearing transcript. Not a model."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass

TURN_RE = re.compile(r"^\[(?P<time>\d{2}:\d{2}:\d{2})\]\s+(?P<speaker>[A-Z][A-Z ]*):\s+(?P<text>.*)$")
DATE_RE = re.compile(
    r"\b(?:\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}|(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},\s+\d{4})\b"
)
MOTION_RE = re.compile(r"\b(moves to|motion to|the motion|is there a motion|seconds the motion|i move)\b", re.I)
OBJECTION_RE = re.compile(r"\b(I object|objection)\b", re.I)
VOTE_RE = re.compile(r"\b(the vote is|all in favour|all in favor|motion is carried)\b", re.I)

ALIASES = [
    ("Northline Data Limited", "applicant"),
    ("Priya Shah", "applicant"),
    ("the applicant", "applicant"),
    ("Planning Committee", "committee"),
    ("the committee", "committee"),
    ("the chair", "committee"),
    ("Elena Voss", "officer"),
    ("the case officer", "officer"),
    ("Mara Ellison", "objector"),
]


@dataclass
class Turn:
    time: str
    speaker: str
    text: str
    labels: list[str]
    dates: list[str]


def parse_turns(text: str) -> list[Turn]:
    turns = []
    for line in text.splitlines():
        if not line.strip():
            continue
        match = TURN_RE.match(line.strip())
        if not match:
            continue
        body = match.group("text")
        labels = []
        if MOTION_RE.search(body):
            labels.append("motion")
        if OBJECTION_RE.search(body):
            labels.append("objection")
        if VOTE_RE.search(body):
            labels.append("vote")
        dates = DATE_RE.findall(body)
        if dates:
            labels.append("date")
        turns.append(Turn(match.group("time"), match.group("speaker"), body, labels, dates))
    return turns


def cluster_entities(text: str) -> dict[str, list[str]]:
    found: dict[str, set[str]] = {}
    occupied = [False] * len(text)
    for phrase, cluster in sorted(ALIASES, key=lambda item: len(item[0]), reverse=True):
        start = 0
        while True:
            index = text.lower().find(phrase.lower(), start)
            if index < 0:
                break
            end = index + len(phrase)
            if not any(occupied[index:end]):
                for i in range(index, end):
                    occupied[i] = True
                found.setdefault(cluster, set()).add(text[index:end])
            start = end
    return {key: sorted(values) for key, values in sorted(found.items())}


def render_timeline(turns: list[Turn]) -> str:
    lines = [
        "# Hearing timeline",
        "",
        "Rules only. Sarcasm and interrupted speech are missed. A model pass is optional and can hallucinate a vote that was not taken.",
        "",
        "| Time | Speaker | Labels | What was said |",
        "| --- | --- | --- | --- |",
    ]
    for turn in turns:
        if not turn.labels:
            continue
        snippet = turn.text.replace("|", "/")
        lines.append(f"| {turn.time} | {turn.speaker} | {', '.join(turn.labels)} | {snippet} |")
    lines.append("")
    return "\n".join(lines)


def label_with_model(turn: Turn) -> str:
    """Optional. Uses rules unless OPENAI_BASE_URL and OPENAI_API_KEY are set."""
    import os

    if not (os.environ.get("OPENAI_BASE_URL") and os.environ.get("OPENAI_API_KEY")):
        if "motion" in turn.labels or "?" in turn.text and turn.speaker == "CHAIR":
            return "question" if turn.text.strip().endswith("?") else "ruling" if "Overruled" in turn.text or "vote" in turn.labels else "statement"
        if turn.speaker in {"STAFF", "APPLICANT", "NEIGHBOR", "MEMBER"} and not turn.text.strip().endswith("?"):
            return "answer"
        return "statement"
    import json
    import urllib.request

    prompt = f"Label this hearing turn as question, answer, or ruling. Reply with one word.\n{turn.speaker}: {turn.text}"
    body = json.dumps({"model": os.environ.get("OPENAI_MODEL", "gpt-4o-mini"), "messages": [{"role": "user", "content": prompt}], "temperature": 0}).encode()
    req = urllib.request.Request(
        os.environ["OPENAI_BASE_URL"].rstrip("/") + "/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode())
    word = payload["choices"][0]["message"]["content"].strip().split()[0].lower()
    return word if word in {"question", "answer", "ruling"} else "statement"

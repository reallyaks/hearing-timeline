# hearing-timeline

Turns a timestamped hearing transcript into a timeline and an entity list. The sample is a 40-line fictional planning-board hearing about a data-center permit. Nobody in it is real.

## Run

```bash
python -m hearing_timeline samples/hearing.txt --out-dir /tmp/hearing
python -m unittest discover -s tests
```

Committed outputs, so you can read them with no command:

- [samples/timeline.md](samples/timeline.md)
- [samples/entities.json](samples/entities.json)

Extraction is rules plus a few regular expressions: motion, objection, vote, and dates like `February 9, 2026`. Repeated names are clustered (applicant, board, staff, neighbor) by longest match first.

## One tradeoff

Rules miss sarcasm and interrupted speech. An optional model pass can label a turn as question, answer, or ruling, but only if both `OPENAI_BASE_URL` and `OPENAI_API_KEY` are set. That pass is slower and can hallucinate a vote that was not taken. Leave the variables unset and the tool stays on the rules.

Not legal advice. Not a transcript service.

# hearing-timeline

Turns a timestamped transcript into a timeline and an entity list. The sample is a 40-line fictional meeting of a planning committee on an application for planning permission. The people and the site are invented.

## Run

```bash
python -m hearing_timeline samples/hearing.txt --out-dir /tmp/hearing
python -m unittest discover -s tests
```

Committed outputs, so you can read them with no command:

- [samples/timeline.md](samples/timeline.md)
- [samples/entities.json](samples/entities.json)

Extraction is rules plus a few regular expressions: motion, objection, vote, and dates like `9 February 2026`. Repeated names are clustered (applicant, committee, officer, objector) by longest match first.

## Tradeoff

Rules miss sarcasm and interrupted speech. A model pass can label a turn as question, answer, or ruling, but only if both `OPENAI_BASE_URL` and `OPENAI_API_KEY` are set. That pass is slower and can label a vote that was not taken. Leave the variables unset and the tool stays on the rules.

import json
from pathlib import Path

from hearing_timeline.engine import cluster_entities, parse_turns, render_timeline

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("transcript")
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()
    text = Path(args.transcript).read_text()
    turns = parse_turns(text)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "timeline.md").write_text(render_timeline(turns))
    (out / "entities.json").write_text(json.dumps(cluster_entities(text), indent=2) + "\n")
    print(f"{len(turns)} turns")

if __name__ == "__main__":
    main()

# gitblame-wrapped

> **Your annual developer personality report — from your own git history.**

Like Spotify Wrapped, but for your coding habits. `gitblame-wrapped` digs through your git log and generates a snarky, honest report: your peak commit hours, your panic-commit rate, your vague message count, and — most importantly — your **developer archetype**.

---

## Features

- Parses any local git repository — no API keys, no cloud, no nonsense
- Hourly commit heatmap (ASCII bar chart)
- "Shame section": late-night commits, panic keywords, profanity in messages
- Developer archetype classification (6 types)
- Optional text-file export
- Zero dependencies — pure Python 3.10+ stdlib only

---

## Usage

```bash
# Analyse the current repo for the current year
python gitblame_wrapped.py

# Analyse a specific repo and year
python gitblame_wrapped.py /path/to/repo --year 2023

# Save the report to a file
python gitblame_wrapped.py . --year 2024 --output report.txt
```

### Example output

```
╔══════════════════════════════════════════════════════════╗
║                  GITBLAME WRAPPED  2024                  ║
║                       my-project                         ║
╚══════════════════════════════════════════════════════════╝

  YOUR DEVELOPER ARCHETYPE
  The Vampire Developer
  The sun is your enemy. Your best commits happen when the
  rest of the world sleeps...

──────────────────────────────────────────────────────────
 BY THE NUMBERS
──────────────────────────────────────────────────────────
  Total commits ..............  847
  Unique contributors ........  3
  Most active author .........  dev@example.com (612 commits)
  Peak commit hour ...........  11:00 PM (94 commits)
  Busiest day of week ........  Wednesday
  Busiest month ..............  October
...
```

---

## Developer Archetypes

| Archetype | Trigger |
|-----------|---------|
| The Chaos Engineer | Night owl **+** high panic-commit rate |
| The Vampire Developer | Heavy late-night commits |
| The Cryptic Committer | >25% vague one-word messages |
| The Diligent Documenter | Long, descriptive messages & calm workflow |
| The Hotfix Hero | >40% fix/hotfix/revert commits |
| The Steady Craftsperson | None of the above — consistently solid |

---

## Requirements

- Python 3.10+
- `git` installed and on your PATH
- A git repository with at least one commit

---

## Why this project?

I built this to practice:
- **subprocess** for spawning and parsing CLI tools
- **argparse** for building ergonomic CLIs
- **Counter / defaultdict** for lightweight data aggregation
- **datetime** parsing across timezones
- Writing readable output without any third-party libraries

---

## License

MIT

# gitblame-wrapped

> **Your annual developer personality report — from your own git history.**

I built this over a weekend after wondering what my commit history said about me (turns out, nothing flattering). It's basically Spotify Wrapped but for your coding habits — point it at a repo and it digs through a year of commits to tell you when you actually work, how you write commit messages, and what kind of developer that makes you.

Runs entirely on your machine against your local `.git` history. No accounts, no telemetry, no cloud round-trip — just your own history, turned back on you.

---

## Features

- Parses any local git repository — no API keys, no cloud, no nonsense
- Hourly commit heatmap (ASCII bar chart)
- "Shame section": late-night commits, panic keywords, profanity in messages
- Developer archetype classification (6 types)
- Optional text-file export
- Zero dependencies — pure Python 3.10+ stdlib only

---

## Installation

```bash
git clone https://github.com/yourname/gitblame-wrapped.git
cd gitblame-wrapped
```

That's it. No `pip install`, no venv, no lockfile to fight with — just Python 3.10+ and the standard library. I wanted this to be something I could drop into any repo without thinking twice.

---

## Usage

```bash
python gitblame_wrapped.py <path-to-repo> [--year YYYY] [--output report.txt]
```

**Example:**

```bash
python gitblame_wrapped.py . --year 2024 --output report.txt
```

| Flag | Description | Default |
|------|-------------|---------|
| `path` | Path to the local git repository | *(required)* |
| `--year` | Limit the report to a specific year | current year |
| `--output` | Write the report to a text file | stdout only |

---

## Sample Output

```
╔══════════════════════════════════════════════════════════╗
║                GITBLAME WRAPPED — 2024                   ║
║                       my-project                         ║
╚══════════════════════════════════════════════════════════╝

 YOUR DEVELOPER ARCHETYPE
 ────────────────────────
   The Vampire Developer

   The sun is your enemy. Your best commits happen when the
   rest of the world sleeps.

──────────────────────────────────────────────────────────
  BY THE NUMBERS
──────────────────────────────────────────────────────────
  Total commits ..............  847
  Unique contributors ........  3
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

## How It Works

Nothing fancy under the hood — it just reads commit metadata straight from `git log` (timestamps, authors, messages) for whatever repo and year you point it at, then:

1. Buckets commits by hour of day to build the heatmap
2. Scans commit messages for panic keywords (`fix`, `oops`, `urgent`, profanity, etc.)
3. Scores message length and descriptiveness
4. Runs the aggregated stats through the archetype rules above

Your data never leaves your machine — it's all local `git log` parsing, nothing gets sent anywhere.

---

## Why I Made This

Mostly curiosity, partly self-shame. I had a hunch my commit timestamps would be embarrassing and I was right. If you run this on your own repo and don't like what it says about you, that's between you and your commit history, not me.

## Contributing

This started as a personal tool, so it's a little rough around the edges — but if you've got an idea for a new archetype, a better heuristic, or you just want to poke at the code, issues and PRs are genuinely welcome. If you're proposing a new archetype, throw the trigger logic in the issue first so we can hash it out before you write code.

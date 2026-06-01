#!/usr/bin/env python3
"""
gitblame-wrapped: Your annual developer personality report.
Analyzes git history and roasts your coding habits.
"""

import subprocess
import re
import sys
import argparse
from datetime import datetime, timezone
from collections import Counter, defaultdict
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────────────

def run_git(args: list[str], cwd: str) -> str:
    result = subprocess.run(
        ["git"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        sys.exit(f"[git error] {result.stderr.strip()}")
    return result.stdout.strip()


def parse_log(repo: str, year: int) -> list[dict]:
    """Return a list of commit dicts for the given year."""
    since = f"{year}-01-01"
    until = f"{year}-12-31"
    fmt = "%H|%ae|%s|%ci|%ad"  # hash | email | subject | commit-iso | author-date-iso

    raw = run_git(
        ["log", f"--since={since}", f"--until={until}",
         f"--format={fmt}", "--date=format:%H"],
        cwd=repo,
    )
    if not raw:
        return []

    commits = []
    for line in raw.splitlines():
        parts = line.split("|", 4)
        if len(parts) < 5:
            continue
        sha, email, subject, ci_date_str, ad_date_str = parts
        try:
            commit_dt = datetime.fromisoformat(ci_date_str.strip())
        except ValueError:
            continue
        commits.append({
            "sha": sha,
            "email": email.lower(),
            "subject": subject,
            "hour": commit_dt.hour,
            "weekday": commit_dt.strftime("%A"),
            "month": commit_dt.strftime("%B"),
            "month_num": commit_dt.month,
        })
    return commits


# ── Stats ─────────────────────────────────────────────────────────────────────

def compute_stats(commits: list[dict]) -> dict:
    if not commits:
        return {}

    hours = [c["hour"] for c in commits]
    weekdays = [c["weekday"] for c in commits]
    months = [c["month_num"] for c in commits]
    subjects = [c["subject"] for c in commits]
    authors = Counter(c["email"] for c in commits)

    hour_counts = Counter(hours)
    peak_hour = hour_counts.most_common(1)[0][0]

    def hour_label(h: int) -> str:
        suffix = "AM" if h < 12 else "PM"
        return f"{h % 12 or 12}:00 {suffix}"

    # Shame metrics
    late_night = sum(1 for h in hours if 0 <= h < 5)
    panic_keywords = re.compile(
        r"\b(fix|hotfix|urgent|oops|revert|broken|crash|bug|typo|sorry|wip|temp|hack|todo|quick)\b",
        re.IGNORECASE,
    )
    panic_commits = sum(1 for s in subjects if panic_keywords.search(s))
    swear_pattern = re.compile(r"\b(wtf|damn|shit|crap|hell|ugh|argh|fml)\b", re.IGNORECASE)
    swear_commits = sum(1 for s in subjects if swear_pattern.search(s))

    # Message quality
    one_word = sum(1 for s in subjects if len(s.split()) == 1)
    vague = sum(1 for s in subjects if s.lower() in {
        "update", "changes", "stuff", "misc", "wip", "fix", "fixes", "done", "ok", "test"
    })

    avg_msg_len = sum(len(s) for s in subjects) / len(subjects)

    longest_msg = max(subjects, key=len)
    shortest_msg = min(subjects, key=len)

    # Busiest month
    month_counts = Counter(months)
    busiest_month_num = month_counts.most_common(1)[0][0]
    busiest_month = datetime(2000, busiest_month_num, 1).strftime("%B")

    return {
        "total": len(commits),
        "authors": authors,
        "top_author": authors.most_common(1)[0],
        "peak_hour": peak_hour,
        "peak_hour_label": hour_label(peak_hour),
        "peak_hour_count": hour_counts[peak_hour],
        "busiest_day": Counter(weekdays).most_common(1)[0][0],
        "busiest_month": busiest_month,
        "late_night_commits": late_night,
        "panic_commits": panic_commits,
        "swear_commits": swear_commits,
        "one_word_messages": one_word,
        "vague_messages": vague,
        "avg_msg_len": avg_msg_len,
        "longest_msg": longest_msg[:80],
        "shortest_msg": shortest_msg,
        "hour_counts": dict(hour_counts),
    }


# ── Personality archetype ─────────────────────────────────────────────────────

def determine_archetype(s: dict) -> tuple[str, str]:
    """Return (title, description) based on commit behaviour."""
    night_pct = s["late_night_commits"] / max(s["total"], 1)
    panic_pct = s["panic_commits"] / max(s["total"], 1)

    if night_pct > 0.25 and panic_pct > 0.30:
        return "🔥 The Chaos Engineer", (
            "You thrive at 2 AM with coffee in one hand and Stack Overflow in the other. "
            "Panic is your workflow. Production is your testing environment."
        )
    if night_pct > 0.20:
        return "🦇 The Vampire Developer", (
            "The sun is your enemy. Your best commits happen when the rest of the world sleeps. "
            "You've probably never attended a morning standup fully awake."
        )
    if s["vague_messages"] > s["total"] * 0.25:
        return "🕵️ The Cryptic Committer", (
            "Your commit history reads like a mystery novel. 'update', 'fix', 'stuff'. "
            "Future-you will have absolutely no idea what past-you did here."
        )
    if s["avg_msg_len"] > 60 and panic_pct < 0.10:
        return "📚 The Diligent Documenter", (
            "You write commit messages like they're cover letters. "
            "Your git log is a joy to bisect. Your teammates quietly love you."
        )
    if panic_pct > 0.40:
        return "🚑 The Hotfix Hero", (
            "You don't write features — you fight fires. "
            "Where others see a bug, you see an opportunity to be a hero. Again."
        )
    return "🛠️ The Steady Craftsperson", (
        "Consistent hours, reasonable commit messages, no major red flags. "
        "You are the developer every team needs and nobody writes blog posts about."
    )


# ── ASCII chart ───────────────────────────────────────────────────────────────

def hourly_bar_chart(hour_counts: dict) -> str:
    if not hour_counts:
        return ""
    max_v = max(hour_counts.values())
    lines = []
    for h in range(24):
        count = hour_counts.get(h, 0)
        bar_len = int((count / max_v) * 20) if max_v else 0
        label = f"{h:02d}:00"
        bar = "█" * bar_len
        lines.append(f"  {label} │{bar:<20} {count}")
    return "\n".join(lines)


# ── Report renderer ───────────────────────────────────────────────────────────

DIVIDER = "─" * 60

def render_report(s: dict, year: int, repo: str) -> str:
    archetype_title, archetype_desc = determine_archetype(s)
    chart = hourly_bar_chart(s["hour_counts"])

    lines = [
        "",
        "╔" + "═" * 58 + "╗",
        f"║{'  🎁  GITBLAME WRAPPED  ' + str(year):^58}║",
        f"║{'  ' + Path(repo).resolve().name:^58}║",
        "╚" + "═" * 58 + "╝",
        "",
        f"  YOUR DEVELOPER ARCHETYPE",
        f"  {archetype_title}",
        f"  {archetype_desc}",
        "",
        DIVIDER,
        f"  📊  BY THE NUMBERS",
        DIVIDER,
        f"  Total commits .............. {s['total']}",
        f"  Unique contributors ........ {len(s['authors'])}",
        f"  Most active author ......... {s['top_author'][0]} ({s['top_author'][1]} commits)",
        f"  Peak commit hour ........... {s['peak_hour_label']} ({s['peak_hour_count']} commits)",
        f"  Busiest day of week ........ {s['busiest_day']}",
        f"  Busiest month .............. {s['busiest_month']}",
        "",
        DIVIDER,
        f"  😬  THE SHAME SECTION",
        DIVIDER,
        f"  Late-night commits (12–5 AM). {s['late_night_commits']}",
        f"  Panic/fix keywords ......... {s['panic_commits']}",
        f"  Profanity in messages ...... {s['swear_commits']}",
        f"  One-word messages .......... {s['one_word_messages']}",
        f"  Vague messages ............. {s['vague_messages']}",
        f"  Avg message length ......... {s['avg_msg_len']:.1f} chars",
        "",
        DIVIDER,
        f"  💬  MEMORABLE MESSAGES",
        DIVIDER,
        f"  Longest:   \"{s['longest_msg']}\"",
        f"  Shortest:  \"{s['shortest_msg']}\"",
        "",
        DIVIDER,
        f"  🕐  COMMITS BY HOUR",
        DIVIDER,
        chart,
        "",
        DIVIDER,
        "  Generated by gitblame-wrapped  •  github.com/you/gitblame-wrapped",
        DIVIDER,
        "",
    ]
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="gitblame-wrapped — your annual developer personality report"
    )
    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=datetime.now(timezone.utc).year,
        help="Year to analyse (default: current year)",
    )
    parser.add_argument(
        "--output",
        help="Save report to a text file",
    )
    args = parser.parse_args()

    print(f"\n  Scanning {Path(args.repo).resolve()} for {args.year}…", flush=True)
    commits = parse_log(args.repo, args.year)

    if not commits:
        sys.exit(f"  No commits found in {args.year}. Nothing to report.")

    stats = compute_stats(commits)
    report = render_report(stats, args.year, args.repo)
    print(report)

    if args.output:
        Path(args.output).write_text(report)
        print(f"  Report saved to {args.output}\n")


if __name__ == "__main__":
    main()

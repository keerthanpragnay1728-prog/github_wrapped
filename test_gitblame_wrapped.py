"""
Unit tests for gitblame_wrapped.py
Run with: python -m pytest test_gitblame_wrapped.py -v
"""

import pytest
from gitblame_wrapped import compute_stats, determine_archetype, hourly_bar_chart


# ── Fixtures ──────────────────────────────────────────────────────────────────

def make_commit(hour=10, weekday="Monday", month_num=6, subject="feat: add login"):
    return {
        "sha": "abc123",
        "email": "dev@example.com",
        "subject": subject,
        "hour": hour,
        "weekday": weekday,
        "month": "June",
        "month_num": month_num,
    }


NORMAL_COMMITS = [make_commit(hour=10, subject=f"feat: change {i}") for i in range(20)]
NIGHT_OWL_COMMITS = [make_commit(hour=2, subject="fix: something") for _ in range(10)]
PANIC_COMMITS = [make_commit(subject="hotfix: URGENT broken prod") for _ in range(15)]
VAGUE_COMMITS = [make_commit(subject="update") for _ in range(10)]


# ── compute_stats ─────────────────────────────────────────────────────────────

class TestComputeStats:
    def test_returns_empty_on_no_commits(self):
        assert compute_stats([]) == {}

    def test_total_count(self):
        stats = compute_stats(NORMAL_COMMITS)
        assert stats["total"] == 20

    def test_author_count(self):
        commits = NORMAL_COMMITS + [make_commit() | {"email": "other@x.com"}]
        stats = compute_stats(commits)
        assert len(stats["authors"]) == 2

    def test_top_author(self):
        stats = compute_stats(NORMAL_COMMITS)
        assert stats["top_author"][0] == "dev@example.com"

    def test_peak_hour_detection(self):
        early = [make_commit(hour=9) for _ in range(5)]
        late = [make_commit(hour=23) for _ in range(15)]
        stats = compute_stats(early + late)
        assert stats["peak_hour"] == 23

    def test_late_night_count(self):
        commits = [make_commit(hour=3) for _ in range(7)] + NORMAL_COMMITS
        stats = compute_stats(commits)
        assert stats["late_night_commits"] == 7

    def test_panic_commit_detection(self):
        commits = [make_commit(subject="hotfix: broken!") for _ in range(5)]
        stats = compute_stats(commits)
        assert stats["panic_commits"] == 5

    def test_swear_detection(self):
        commits = [make_commit(subject="wtf why is this broken") for _ in range(3)]
        stats = compute_stats(commits)
        assert stats["swear_commits"] == 3

    def test_vague_message_count(self):
        commits = [make_commit(subject="update") for _ in range(4)] + \
                  [make_commit(subject="fix") for _ in range(2)]
        stats = compute_stats(commits)
        assert stats["vague_messages"] == 6

    def test_avg_message_length(self):
        commits = [make_commit(subject="ab") for _ in range(10)]
        stats = compute_stats(commits)
        assert stats["avg_msg_len"] == pytest.approx(2.0)


# ── determine_archetype ───────────────────────────────────────────────────────

class TestDetermineArchetype:
    def _stats_with(self, total, late_night, panic, vague=0, avg_len=30):
        return {
            "total": total,
            "late_night_commits": late_night,
            "panic_commits": panic,
            "vague_messages": vague,
            "avg_msg_len": avg_len,
        }

    def test_chaos_engineer(self):
        s = self._stats_with(total=100, late_night=30, panic=35)
        title, _ = determine_archetype(s)
        assert "Chaos" in title

    def test_vampire_developer(self):
        s = self._stats_with(total=100, late_night=25, panic=5)
        title, _ = determine_archetype(s)
        assert "Vampire" in title

    def test_cryptic_committer(self):
        s = self._stats_with(total=100, late_night=2, panic=5, vague=30)
        title, _ = determine_archetype(s)
        assert "Cryptic" in title

    def test_diligent_documenter(self):
        s = self._stats_with(total=100, late_night=2, panic=5, vague=2, avg_len=80)
        title, _ = determine_archetype(s)
        assert "Diligent" in title

    def test_hotfix_hero(self):
        s = self._stats_with(total=100, late_night=2, panic=45)
        title, _ = determine_archetype(s)
        assert "Hotfix" in title

    def test_steady_craftsperson_fallthrough(self):
        s = self._stats_with(total=100, late_night=2, panic=5, vague=5, avg_len=35)
        title, _ = determine_archetype(s)
        assert "Steady" in title

    def test_archetype_returns_non_empty_description(self):
        s = self._stats_with(total=100, late_night=5, panic=5)
        _, desc = determine_archetype(s)
        assert len(desc) > 20


# ── hourly_bar_chart ──────────────────────────────────────────────────────────

class TestHourlyBarChart:
    def test_returns_empty_string_on_empty_input(self):
        assert hourly_bar_chart({}) == ""

    def test_contains_all_24_hours(self):
        chart = hourly_bar_chart({10: 5, 22: 10})
        for h in range(24):
            assert f"{h:02d}:00" in chart

    def test_peak_hour_has_longest_bar(self):
        chart = hourly_bar_chart({10: 1, 22: 100})
        lines = chart.splitlines()
        bar_lengths = {
            line.split("│")[0].strip(): len(line.split("│")[1].rstrip().split()[0])
            for line in lines if "│" in line
        }
        assert bar_lengths.get("22:00", 0) >= bar_lengths.get("10:00", 0)

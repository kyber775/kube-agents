"""Contract tests for front-door board-reading instructions and constraints.

Asserts that agents/chat/SOUL.md §1.5 explicitly instructs the model that
kanban_list without status/assignee filters returns tasks oldest-first and
cannot reach the newest card on boards exceeding a single page (issue #1048).
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CHAT_SOUL = REPO_ROOT / "agents/chat/SOUL.md"
AUTOOPS_TASK = REPO_ROOT / "bench/tasks/autoops-warning-event-triage/task.yaml"


class ChatBoardReadContractTest(unittest.TestCase):
    def test_soul_states_kanban_list_filter_constraint(self) -> None:
        text = CHAT_SOUL.read_text(encoding="utf-8")
        # Ensure Section 1.5 exists
        self.assertIn("## 1.5 Reading & Managing the Board", text)

        # Extract section 1.5
        section_match = re.search(
            r"## 1\.5 Reading & Managing the Board(.*?)(?:\n---|\n## |\Z)",
            text,
            re.DOTALL,
        )
        self.assertIsNotNone(section_match, "Section 1.5 missing from agents/chat/SOUL.md")
        assert section_match is not None
        section = section_match.group(1)

        # The persona must not frame status filtering as merely an optional style preference
        # when the ask is narrow; it must state the structural constraint that bare calls return oldest-first.
        self.assertNotIn(
            "pass `status` and/or `assignee` filters when the ask is narrow",
            section,
            "agents/chat/SOUL.md §1.5 should not imply filters are merely optional when the ask is narrow",
        )

        # Must explicitly warn that bare calls return oldest-first and miss the newest card
        self.assertRegex(
            section,
            re.compile(r"oldest-first", re.IGNORECASE),
            "agents/chat/SOUL.md §1.5 must explain that bare calls return oldest-first",
        )
        self.assertRegex(
            section,
            re.compile(r"newest card", re.IGNORECASE),
            "agents/chat/SOUL.md §1.5 must explain that the newest card will not be in the response",
        )

        # Must instruct to pass status and/or assignee filters
        self.assertRegex(
            section,
            re.compile(r"status.*filter", re.IGNORECASE),
            "agents/chat/SOUL.md §1.5 must instruct to pass status filters",
        )

    def test_autoops_task_references_kanban_list_decision(self) -> None:
        text = AUTOOPS_TASK.read_text(encoding="utf-8")
        self.assertIn(
            "1048",
            text,
            "bench/tasks/autoops-warning-event-triage/task.yaml must reference #1048 in its kanban_list rationale",
        )


if __name__ == "__main__":
    unittest.main()

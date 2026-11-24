"""Contract tests for the public scenarios workspace and private ignore boundary."""

from __future__ import annotations

import json
import re
import subprocess
import tomllib
from pathlib import Path

from support import ScriptedCallbacks

import tome

REPO_ROOT = Path(__file__).resolve().parents[1]
SCENARIOS_DIR = REPO_ROOT / "scenarios"
PUBLIC_SCENARIO_DOCS = (
    SCENARIOS_DIR / "README.md",
    SCENARIOS_DIR / "scenario_template.md",
    SCENARIOS_DIR / "examples" / "actor_a_actor_b.md",
)
PERSONAL_PATH_RE = re.compile(r"/(?:Users|home)/")
HEADING_RE = re.compile(r"^#{1,6}\s+\S")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]+\]\(([^)]+)\)")
INLINE_CODE_RE = re.compile(r"`[^`]*`")
MULTI_SENTENCE_RE = re.compile(r"[.!?][\"')]*\s+[A-Z]")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]")


def _git(*args: str, cwd: Path = REPO_ROOT, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "--no-pager", *args],
        cwd=cwd,
        check=check,
        capture_output=True,
        text=True,
    )


def _iter_non_code_lines(markdown_text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    in_fence = False
    for line_no, line in enumerate(markdown_text.splitlines(), start=1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence:
            lines.append((line_no, line))
    return lines


def _extract_h2_sections(markdown_text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for _, line in _iter_non_code_lines(markdown_text):
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def _find_section(sections: dict[str, list[str]], prefix: str) -> list[str]:
    for heading, body in sections.items():
        if heading == prefix or heading.startswith(f"{prefix} "):
            return body
    raise AssertionError(f"Missing section starting with {prefix!r}.")


def _strip_code_ticks(value: str) -> str:
    stripped = value.strip()
    if len(stripped) >= 2 and stripped.startswith("`") and stripped.endswith("`"):
        return stripped[1:-1]
    return stripped


def _translate_scenario_markdown(path: Path) -> tuple[tome.WorldState, tome.RunRequest, str]:
    sections = _extract_h2_sections(path.read_text(encoding="utf-8"))

    settings: dict[str, str] = {}
    for line in _find_section(sections, "Run Settings"):
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if len(cells) != 2 or cells[0] == "Setting" or set(cells[0]) <= {":", "-"}:
            continue
        settings[cells[0]] = _strip_code_ticks(cells[1])

    actors: list[tome.Actor] = []
    current_fields: dict[str, str] | None = None
    for line in _find_section(sections, "Actors"):
        stripped = line.strip()
        if stripped.startswith("### "):
            if current_fields is not None:
                actors.append(tome.Actor(**current_fields))
            current_fields = {}
        elif current_fields is not None and stripped.startswith("- "):
            key, sep, raw_value = stripped[2:].partition(":")
            if sep:
                field_map = {"ID": "id", "Name": "name", "Agenda": "agenda"}
                if key.strip() in field_map:
                    current_fields[field_map[key.strip()]] = _strip_code_ticks(raw_value)
    if current_fields is not None:
        actors.append(tome.Actor(**current_fields))

    canon_facts = [
        line.strip()[2:].strip()
        for line in _find_section(sections, "Starting Canon Facts")
        if line.strip().startswith("- ")
    ]

    world_state = tome.WorldState(
        session_index=int(settings["Starting session index"]),
        turn_index=int(settings["Starting turn index"]),
        canon_facts=canon_facts,
        actors=actors,
    )
    spark_setting = settings["Spark tables"]
    if spark_setting != "Built-in defaults":
        raise ValueError(f"Unsupported spark table setting: {spark_setting!r}")

    request = tome.RunRequest(
        contract_version=settings["Contract version"],
        world_state=world_state,
        turn_count=int(settings["Number of turns"]),
        first_round_order=json.loads(settings["Actor order"]),
        seed=int(settings["Random seed"]),
    )
    return world_state, request, spark_setting


def test_scenarios_workspace_structure_and_git_tracking() -> None:
    for doc_path in PUBLIC_SCENARIO_DOCS:
        assert doc_path.is_file(), (
            f"Expected public scenario file: {doc_path.relative_to(REPO_ROOT)}"
        )

    assert not (REPO_ROOT / "docs" / "scenarios").exists()
    assert _git("ls-files", "--", "scenarios/private").stdout.strip() == ""
    assert _git("ls-files", "--", "docs/scenarios").stdout.strip() == ""

    root_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/scenarios" not in root_readme
    assert "scenarios/README.md" in root_readme
    assert "scenarios/scenario_template.md" in root_readme
    assert "scenarios/examples/actor_a_actor_b.md" in root_readme
    assert "scenarios/private/" in root_readme


def test_public_scenario_markdown_formatting_links_and_hygiene() -> None:
    checked_docs = (*PUBLIC_SCENARIO_DOCS, REPO_ROOT / "README.md")
    private_root = (SCENARIOS_DIR / "private").resolve()

    for doc_path in checked_docs:
        assert doc_path.is_file(), f"Missing Markdown file: {doc_path.relative_to(REPO_ROOT)}"
        content = doc_path.read_text(encoding="utf-8")
        rel_doc = doc_path.relative_to(REPO_ROOT)

        assert PERSONAL_PATH_RE.search(content) is None, f"Personal path found in {rel_doc}"
        assert EMOJI_RE.search(content) is None, f"Emoji found in {rel_doc}"

        raw_lines = content.splitlines()
        in_fence = False
        for idx, line in enumerate(raw_lines):
            if line.lstrip().startswith("```"):
                in_fence = not in_fence
                continue
            if not in_fence and HEADING_RE.match(line):
                assert idx + 1 < len(raw_lines) and raw_lines[idx + 1] == "", (
                    f"Heading at {rel_doc}:{idx + 1} must be followed by a blank line."
                )

        for line_no, line in _iter_non_code_lines(content):
            for raw_target in MARKDOWN_LINK_RE.findall(line):
                target = raw_target.strip().split()[0]
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_part, _, _ = target.partition("#")
                resolved = (doc_path.parent / path_part).resolve()
                assert resolved.is_relative_to(REPO_ROOT), (
                    f"Link {target!r} at {rel_doc}:{line_no} escapes repository root."
                )
                assert not resolved.is_relative_to(private_root), (
                    f"Link {target!r} at {rel_doc}:{line_no} targets scenarios/private/."
                )
                assert resolved.exists(), (
                    f"Link {target!r} at {rel_doc}:{line_no} does not resolve to an existing file."
                )
                ignore_probe = _git(
                    "check-ignore",
                    "-q",
                    str(resolved.relative_to(REPO_ROOT)),
                    check=False,
                )
                assert ignore_probe.returncode == 1, (
                    f"Link {target!r} at {rel_doc}:{line_no} resolves to an ignored path."
                )

    for doc_path in PUBLIC_SCENARIO_DOCS:
        content = doc_path.read_text(encoding="utf-8")
        rel_doc = doc_path.relative_to(REPO_ROOT)
        for line_no, line in _iter_non_code_lines(content):
            stripped = line.strip()
            if not stripped or HEADING_RE.match(stripped) or stripped.startswith("|"):
                continue
            scrubbed = INLINE_CODE_RE.sub("code", stripped)
            scrubbed = MARKDOWN_LINK_RE.sub("link", scrubbed)
            assert MULTI_SENTENCE_RE.search(scrubbed) is None, (
                f"Multiple sentences on one line at {rel_doc}:{line_no}: {line!r}"
            )


def test_public_scenario_licensing_and_boundary_documentation() -> None:
    for doc_path in PUBLIC_SCENARIO_DOCS:
        content = doc_path.read_text(encoding="utf-8")
        rel_doc = doc_path.relative_to(REPO_ROOT)
        for required_term in ("CC BY-SA 4.0", "Triple-O", "Cezar Capacle", "Chris Engle"):
            assert required_term in content, f"Missing {required_term!r} in {rel_doc}"
        assert "Matrix Games" in content, f"Missing Matrix Games attribution in {rel_doc}"

    scenarios_readme = (SCENARIOS_DIR / "README.md").read_text(encoding="utf-8")
    for expected in (
        "scenario_template.md",
        "examples/",
        "private/",
        "WorldState",
        "RunRequest",
        "mkdir -p scenarios/private",
        "log.jsonl",
        "git add -f",
        "MIT",
    ):
        assert expected in scenarios_readme

    lower_readme = scenarios_readme.lower()
    assert "not encryption" in lower_readme
    assert "access control" in lower_readme
    assert "already tracked" in lower_readme
    assert "external service" in lower_readme
    assert "inherit" in lower_readme
    assert "relicense" in lower_readme
    assert "rewriting git history" in lower_readme or "rewrite git history" in lower_readme


def test_gitignore_covers_private_subtree_synthetically(tmp_path: Path) -> None:
    gitignore_path = REPO_ROOT / ".gitignore"
    gitignore_text = gitignore_path.read_text(encoding="utf-8")
    gitignore_lines = [line.strip() for line in gitignore_text.splitlines() if line.strip()]

    assert "/scenarios/private/" in gitignore_lines
    assert "docs/scenarios" not in gitignore_text
    assert PERSONAL_PATH_RE.search(gitignore_text) is None

    synthetic_ignored_paths = (
        "scenarios/private/synthetic_case/scenario.md",
        "scenarios/private/synthetic_case/nested/state.json",
        "scenarios/private/synthetic_case/nested/log.jsonl",
        "scenarios/private/synthetic_case/attachments/diagram.png",
        "scenarios/private/synthetic_case/REPLAY.md",
    )
    for rel_path in synthetic_ignored_paths:
        probe = _git("check-ignore", "-q", rel_path, check=False)
        assert probe.returncode == 0, f"Expected {rel_path} to be ignored by .gitignore"

    public_unignored_paths = (
        "scenarios/README.md",
        "scenarios/scenario_template.md",
        "scenarios/examples/actor_a_actor_b.md",
    )
    for rel_path in public_unignored_paths:
        probe = _git("check-ignore", "-q", rel_path, check=False)
        assert probe.returncode == 1, f"Expected {rel_path} not to be ignored by .gitignore"

    _git("init", "-q", cwd=tmp_path)
    (tmp_path / ".gitignore").write_text(gitignore_text, encoding="utf-8")

    synthetic_files = {
        "scenarios/private/synthetic/scenario.md": "# Synthetic private scenario\n",
        "scenarios/private/synthetic/nested/state.json": '{"session_index": 0}\n',
        "scenarios/private/synthetic/nested/log.jsonl": '{"turn_index": 1}\n',
        "scenarios/private/synthetic/attachments/diagram.png": "synthetic-binary-placeholder\n",
        "scenarios/private/synthetic/REPLAY.md": "# Synthetic replay\n",
        "scenarios/examples/sample.md": "# Public sample\n",
    }
    for rel_path, text_body in synthetic_files.items():
        file_path = tmp_path / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(text_body, encoding="utf-8")

    _git("add", ".", cwd=tmp_path)
    staged = sorted(_git("diff", "--cached", "--name-only", cwd=tmp_path).stdout.splitlines())
    assert staged == [".gitignore", "scenarios/examples/sample.md"]


def test_packaging_and_test_discovery_exclude_private_scenarios() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    testpaths = pyproject["tool"]["pytest"]["ini_options"]["testpaths"]
    assert testpaths == ["tests"]
    assert all("scenarios" not in entry for entry in testpaths)

    assert pyproject["build-system"]["build-backend"] == "hatchling.build"
    hatch_targets = pyproject.get("tool", {}).get("hatch", {}).get("build", {}).get("targets", {})
    wheel_packages = hatch_targets.get("wheel", {}).get(
        "packages", [f"src/{pyproject['project']['name']}"]
    )
    assert wheel_packages == ["src/tome"]
    assert (REPO_ROOT / "src" / "tome").is_dir()
    assert "scenarios" not in json.dumps(hatch_targets)


def test_public_example_translates_and_runs_deterministically() -> None:
    template_text = (SCENARIOS_DIR / "scenario_template.md").read_text(encoding="utf-8")
    example_path = SCENARIOS_DIR / "examples" / "actor_a_actor_b.md"
    example_text = example_path.read_text(encoding="utf-8")

    assert "- [ ]" in template_text
    assert "- [x]" in example_text
    assert "- [ ]" not in example_text
    assert "not a file" in example_text.lower() or "not loaded natively" in example_text.lower()

    world_state, request, spark_setting = _translate_scenario_markdown(example_path)

    assert spark_setting == "Built-in defaults"
    assert request.contract_version == "1.1.0"
    assert request.turn_count == 4
    assert request.seed == 42
    assert request.first_round_order == ["actor_a", "actor_b"]
    assert world_state.session_index == 0
    assert world_state.turn_index == 0
    assert [actor.model_dump() for actor in world_state.actors] == [
        {
            "id": "actor_a",
            "name": "Actor A",
            "agenda": (
                "Wants to maintain continuity of supply while preserving cancellation flexibility."
            ),
        },
        {
            "id": "actor_b",
            "name": "Actor B",
            "agenda": (
                "Wants to secure a bounded supply agreement with a minimum purchase commitment "
                "and no early-cancellation right."
            ),
        },
    ]
    assert world_state.canon_facts == [
        (
            "Actor B has made a standing offer to Actor A for three months of supply, "
            "conditional on a minimum purchase commitment and with no early-cancellation right."
        ),
        "Actor A can accept the standing offer without obtaining further approval from Actor B.",
        "Actor A needs continuity of supply but prefers cancellation flexibility.",
        "Actor A has not yet accepted a replacement supply agreement.",
    ]

    world_snapshot = world_state.model_dump(mode="json")
    request_snapshot = request.model_dump(mode="json", exclude_none=True)

    callbacks_first = ScriptedCallbacks()
    result_first = tome.run(
        request,
        callbacks_first.proposal_generator,
        callbacks_first.peer_reviewer,
        callbacks_first.failure_resolver,
    )

    callbacks_second = ScriptedCallbacks()
    result_second = tome.run(
        request,
        callbacks_second.proposal_generator,
        callbacks_second.peer_reviewer,
        callbacks_second.failure_resolver,
    )

    assert len(result_first.turn_records) == 4
    assert all(isinstance(record, tome.TurnRecord) for record in result_first.turn_records)
    assert [record.active_actor_id for record in result_first.turn_records] == [
        "actor_a",
        "actor_b",
        "actor_a",
        "actor_b",
    ]
    assert result_first.spark_table_source == tome.DEFAULT_TABLE_SET_ID
    assert len(result_first.final_world_state.canon_facts) == 8
    assert result_second == result_first
    assert world_state.model_dump(mode="json") == world_snapshot
    assert request.model_dump(mode="json", exclude_none=True) == request_snapshot

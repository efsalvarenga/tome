"""Contract tests for the public scenarios workspace and private ignore boundary."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tomllib
from collections.abc import Mapping
from pathlib import Path

import pytest
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
FENCE_OPEN_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
INLINE_CODE_SPAN_RE = re.compile(r"(`+)[^`]*?\1")
INLINE_LINK_RE = re.compile(r"!?\[(?:[^\[\]]|\[[^\[\]]*\])*\]\(([^)]*)\)")
REF_LINK_DEF_RE = re.compile(r"^\s*\[[^\]]+\]:\s*(.+?)\s*$")
EMOJI_RE = re.compile(r"[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F1E6-\U0001F1FF]")


def _has_repo_git() -> bool:
    return shutil.which("git") is not None and (REPO_ROOT / ".git").exists()


def _git(
    *args: str,
    cwd: Path = REPO_ROOT,
    check: bool = True,
    env_overrides: Mapping[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_OPTIONAL_LOCKS": "0",
        }
    )
    if env_overrides is not None:
        env.update(env_overrides)
    return subprocess.run(
        ["git", "--no-pager", *args],
        cwd=cwd,
        env=env,
        check=check,
        capture_output=True,
        text=True,
    )


def _public_scenario_docs() -> tuple[Path, ...]:
    docs = set(PUBLIC_SCENARIO_DOCS)
    if _has_repo_git():
        tracked = _git("ls-files", "--", "scenarios/*.md", "scenarios/**/*.md").stdout.splitlines()
        docs.update(REPO_ROOT / rel_path for rel_path in tracked if rel_path)
    return tuple(sorted(docs, key=lambda path: path.as_posix()))


def _non_code_lines(text: str) -> list[tuple[int, str]]:
    lines: list[tuple[int, str]] = []
    fence_char: str | None = None
    opening_len = 0
    for line_no, line in enumerate(text.splitlines(), start=1):
        match = FENCE_OPEN_RE.match(line)
        if fence_char is None:
            if match is not None:
                fence, info = match.groups()
                if fence[0] == "~" or "`" not in info:
                    fence_char = fence[0]
                    opening_len = len(fence)
                    continue
            lines.append((line_no, line))
        elif (
            match is not None
            and match.group(1)[0] == fence_char
            and len(match.group(1)) >= opening_len
            and match.group(2).strip() == ""
        ):
            fence_char = None
            opening_len = 0
    return lines


def test_scenarios_workspace_structure() -> None:
    for doc_path in PUBLIC_SCENARIO_DOCS:
        assert doc_path.is_file(), (
            f"Expected public scenario file: {doc_path.relative_to(REPO_ROOT)}"
        )

    assert not (REPO_ROOT / "docs" / "scenarios").exists()

    root_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/scenarios" not in root_readme
    for expected_ref in (
        "scenarios/README.md",
        "scenarios/scenario_template.md",
        "scenarios/examples/actor_a_actor_b.md",
        "scenarios/private/",
    ):
        assert expected_ref in root_readme

    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    gitignore_lines = [line.strip() for line in gitignore_text.splitlines() if line.strip()]
    assert "/scenarios/private" in gitignore_lines
    assert "/scenarios/private/" in gitignore_lines
    assert gitignore_lines.index("/scenarios/private") < gitignore_lines.index(
        "/scenarios/private/"
    )
    assert "docs/scenarios" not in gitignore_text
    assert PERSONAL_PATH_RE.search(gitignore_text) is None


def test_repo_git_tracking_and_ignore_rules() -> None:
    if not _has_repo_git():
        pytest.skip("Repository .git metadata or git executable is unavailable.")

    assert _git("ls-files", "--", "scenarios/private").stdout.strip() == ""
    assert _git("ls-files", "--", "docs/scenarios").stdout.strip() == ""

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

    for doc_path in _public_scenario_docs():
        rel_path = str(doc_path.relative_to(REPO_ROOT))
        probe = _git("check-ignore", "-q", rel_path, check=False)
        assert probe.returncode == 1, f"Expected {rel_path} not to be ignored by .gitignore"


def test_public_scenario_markdown_formatting_links_and_hygiene() -> None:
    assert _non_code_lines("Top\n~~~~\n```\n# Ignored\n~~~\n~~~~\nEnd\n") == [
        (1, "Top"),
        (7, "End"),
    ]
    assert _non_code_lines("A\n````markdown\n```bash\n```\n````\nB\n") == [
        (1, "A"),
        (6, "B"),
    ]

    checked_docs = (*_public_scenario_docs(), REPO_ROOT / "README.md")
    private_root = (SCENARIOS_DIR / "private").resolve()

    for doc_path in checked_docs:
        assert doc_path.is_file(), f"Missing Markdown file: {doc_path.relative_to(REPO_ROOT)}"
        content = doc_path.read_text(encoding="utf-8")
        rel_doc = doc_path.relative_to(REPO_ROOT)

        assert EMOJI_RE.search(content) is None, f"Emoji found in {rel_doc}"

        raw_lines = content.splitlines()
        for line_no, line in _non_code_lines(content):
            assert PERSONAL_PATH_RE.search(line) is None, (
                f"Personal path found at {rel_doc}:{line_no}"
            )
            if HEADING_RE.match(line):
                assert line_no < len(raw_lines) and raw_lines[line_no] == "", (
                    f"Heading at {rel_doc}:{line_no} must be followed by a blank line."
                )

            scrubbed = INLINE_CODE_SPAN_RE.sub("", line)
            raw_targets = [
                *INLINE_LINK_RE.findall(scrubbed),
                *REF_LINK_DEF_RE.findall(scrubbed),
            ]
            for raw_target in raw_targets:
                tokens = raw_target.strip().split()
                assert tokens, f"Blank link target at {rel_doc}:{line_no}"
                target = tokens[0]
                if target.startswith("<") and target.endswith(">") and len(target) >= 2:
                    target = target[1:-1].strip()
                    assert target, f"Blank angle-bracket link target at {rel_doc}:{line_no}"
                assert not target.lower().startswith("file:"), (
                    f"Disallowed file URI {target!r} at {rel_doc}:{line_no}"
                )
                assert target != "#", f"Empty anchor link at {rel_doc}:{line_no}"
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path_part, _, _ = target.partition("#")
                assert path_part, f"Empty path in link {target!r} at {rel_doc}:{line_no}"
                resolved = (doc_path.parent / path_part).resolve()
                assert resolved.is_relative_to(REPO_ROOT), (
                    f"Link {target!r} at {rel_doc}:{line_no} escapes repository root."
                )
                assert not resolved.is_relative_to(private_root), (
                    f"Link {target!r} at {rel_doc}:{line_no} targets scenarios/private/."
                )
                assert resolved.exists(), (
                    f"Link {target!r} at {rel_doc}:{line_no} does not resolve to an existing path."
                )
                if _has_repo_git() and resolved.is_file():
                    tracked_probe = _git(
                        "ls-files",
                        "--error-unmatch",
                        str(resolved.relative_to(REPO_ROOT)),
                        check=False,
                    )
                    assert tracked_probe.returncode == 0, (
                        f"Link {target!r} at {rel_doc}:{line_no} resolves to an untracked file."
                    )

        assert PERSONAL_PATH_RE.search(content) is None, f"Personal path found in {rel_doc}"


def test_public_scenario_licensing_and_boundary_documentation() -> None:
    required_attribution = (
        "CC BY-SA 4.0",
        "Cezar Capacle",
        "https://capacle.itch.io/triple-o",
        "Chris Engle",
    )
    for doc_path in _public_scenario_docs():
        content = doc_path.read_text(encoding="utf-8")
        rel_doc = doc_path.relative_to(REPO_ROOT)
        for required_term in required_attribution:
            assert required_term in content, f"Missing {required_term!r} in {rel_doc}"

    scenarios_readme = (SCENARIOS_DIR / "README.md").read_text(encoding="utf-8")
    for expected in ("git add -f", "scenarios/private/"):
        assert expected in scenarios_readme


def test_gitignore_covers_private_subtree_synthetically(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    if shutil.which("git") is None:
        pytest.skip("git executable is unavailable.")

    gitignore_text = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    host_index_before = _git("ls-files", "--stage").stdout if _has_repo_git() else None

    poisoned_index = tmp_path / "poisoned_index"
    monkeypatch.setenv("GIT_DIR", str(REPO_ROOT / ".git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(poisoned_index))

    dir_repo = tmp_path / "dir_repo"
    dir_repo.mkdir()
    _git("init", "-q", "--template=", cwd=dir_repo)
    (dir_repo / ".gitignore").write_text(gitignore_text, encoding="utf-8")

    synthetic_files = {
        "scenarios/private/synthetic/scenario.md": "# Synthetic private scenario\n",
        "scenarios/private/synthetic/nested/state.json": '{"session_index": 0}\n',
        "scenarios/private/synthetic/nested/log.jsonl": '{"turn_index": 1}\n',
        "scenarios/private/synthetic/attachments/diagram.png": "synthetic-binary-placeholder\n",
        "scenarios/private/synthetic/REPLAY.md": "# Synthetic replay\n",
        "scenarios/examples/sample.md": "# Public sample\n",
    }
    for rel_path, text_body in synthetic_files.items():
        file_path = dir_repo / rel_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(text_body, encoding="utf-8")

    _git("add", ".", cwd=dir_repo)
    staged = sorted(_git("diff", "--cached", "--name-only", cwd=dir_repo).stdout.splitlines())
    assert staged == [".gitignore", "scenarios/examples/sample.md"]
    assert (dir_repo / ".git").is_dir()
    assert not poisoned_index.exists()

    external_private = tmp_path / "external_private"
    external_private.mkdir()
    (external_private / "scenario.md").write_text("# External private scenario\n", encoding="utf-8")

    symlink_repo = tmp_path / "symlink_repo"
    (symlink_repo / "scenarios" / "examples").mkdir(parents=True)
    _git("init", "-q", "--template=", cwd=symlink_repo)
    (symlink_repo / ".gitignore").write_text(gitignore_text, encoding="utf-8")
    (symlink_repo / "scenarios" / "examples" / "sample.md").write_text(
        "# Public sample\n", encoding="utf-8"
    )

    try:
        os.symlink(external_private, symlink_repo / "scenarios" / "private")
    except (OSError, NotImplementedError):
        pass
    else:
        _git("add", ".", cwd=symlink_repo)
        symlink_staged = sorted(
            _git("diff", "--cached", "--name-only", cwd=symlink_repo).stdout.splitlines()
        )
        assert symlink_staged == [".gitignore", "scenarios/examples/sample.md"]
        assert not poisoned_index.exists()

    if host_index_before is not None:
        assert _git("ls-files", "--stage").stdout == host_index_before


def test_packaging_and_test_discovery_exclude_private_scenarios() -> None:
    pyproject = tomllib.loads((REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    testpaths = pyproject["tool"]["pytest"]["ini_options"]["testpaths"]
    assert testpaths == ["tests"]
    assert all("scenarios" not in entry for entry in testpaths)

    assert pyproject["build-system"]["build-backend"] == "hatchling.build"
    hatch_build = pyproject.get("tool", {}).get("hatch", {}).get("build", {})
    targets = hatch_build.get("targets", {})
    sdist_cfg = targets.get("sdist", {})
    wheel_cfg = targets.get("wheel", {})

    assert not hatch_build.get("ignore-vcs", False)
    assert not sdist_cfg.get("ignore-vcs", False)

    wheel_packages = wheel_cfg.get("packages", [f"src/{pyproject['project']['name']}"])
    assert wheel_packages == ["src/tome"]
    assert (REPO_ROOT / "src" / "tome").is_dir()

    for cfg in (hatch_build, sdist_cfg, wheel_cfg):
        for key in ("force-include", "include", "only-include", "packages"):
            if key in cfg:
                assert "scenarios/private" not in json.dumps(cfg[key])


def test_public_example_runs_deterministically() -> None:
    template_text = (SCENARIOS_DIR / "scenario_template.md").read_text(encoding="utf-8")
    example_text = (SCENARIOS_DIR / "examples" / "actor_a_actor_b.md").read_text(encoding="utf-8")

    assert "`scenarios/README.md`" in template_text
    assert "- [ ]" in template_text
    assert "- [x]" in example_text
    assert "- [ ]" not in example_text

    actor_ids = ["actor_a", "actor_b"]
    canon_facts = [
        (
            "Actor B has made a standing offer to Actor A for three months of supply, "
            "conditional on a minimum purchase commitment and with no early-cancellation right."
        ),
        "Actor A can accept the standing offer without obtaining further approval from Actor B.",
        "Actor A needs continuity of supply but prefers cancellation flexibility.",
        "Actor A has not yet accepted a replacement supply agreement.",
    ]
    for actor_id in actor_ids:
        assert f"`{actor_id}`" in example_text
    for fact in canon_facts:
        assert fact in example_text

    world_state = tome.WorldState(
        session_index=0,
        turn_index=0,
        canon_facts=list(canon_facts),
        actors=[
            tome.Actor(
                id="actor_a",
                name="Actor A",
                agenda=(
                    "Wants to maintain continuity of supply while preserving "
                    "cancellation flexibility."
                ),
            ),
            tome.Actor(
                id="actor_b",
                name="Actor B",
                agenda=(
                    "Wants to secure a bounded supply agreement with a minimum purchase "
                    "commitment and no early-cancellation right."
                ),
            ),
        ],
    )
    request = tome.RunRequest(
        contract_version="1.1.0",
        world_state=world_state,
        turn_count=4,
        first_round_order=list(actor_ids),
        seed=42,
    )

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

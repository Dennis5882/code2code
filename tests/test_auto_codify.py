from pathlib import Path

import pytest

from scripts.auto_codify import PipelineError, collect_reference_files


def test_collect_reference_files_uses_explicit_changed_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    references = tmp_path / "references"
    references.mkdir()
    selected = references / "changed.txt"
    selected.write_text("selected", encoding="utf-8")
    ignored = references / "ignored.txt"
    ignored.write_text("ignored", encoding="utf-8")

    monkeypatch.setenv("REFERENCE_FILES", "references/changed.txt")
    monkeypatch.delenv("REFERENCE_PATTERNS", raising=False)

    files = collect_reference_files()

    assert files == [selected.resolve()]


def test_collect_reference_files_rejects_non_reference_paths(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "references").mkdir()
    (tmp_path / "outside.txt").write_text("x", encoding="utf-8")

    monkeypatch.setenv("REFERENCE_FILES", "outside.txt")

    with pytest.raises(PipelineError):
        collect_reference_files()


def test_collect_reference_files_falls_back_to_patterns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    references = tmp_path / "references"
    references.mkdir()
    included = references / "note.txt"
    included.write_text("hello", encoding="utf-8")
    excluded = references / "diagram.pdf"
    excluded.write_text("pdf placeholder", encoding="utf-8")

    monkeypatch.delenv("REFERENCE_FILES", raising=False)
    monkeypatch.setenv("REFERENCE_PATTERNS", "*.txt")

    files = collect_reference_files()

    assert files == [included.resolve()]
    assert excluded.resolve() not in files

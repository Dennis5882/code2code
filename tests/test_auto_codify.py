from pathlib import Path

import pytest

from scripts.auto_codify import (
    PipelineError,
    call_with_retries,
    collect_reference_files,
    normalize_source_rel_path,
    parse_json_response,
)


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


def test_parse_json_response_accepts_fenced_json() -> None:
    payload = parse_json_response(
        '```json\n{"manual_markdown": "ok", "source_files": []}\n```',
        "test",
    )

    assert payload["manual_markdown"] == "ok"


def test_parse_json_response_extracts_json_object_from_text() -> None:
    payload = parse_json_response(
        'Here is the result:\n{"chunk_label": "chunk_1", "clauses": []}\nThanks.',
        "test",
    )

    assert payload["chunk_label"] == "chunk_1"


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("/src/smoke_trigger.py", "smoke_trigger.py"),
        ("src/wind_load.py", "wind_load.py"),
        ("wind_load.py", "wind_load.py"),
        ("/src/loads/wind.py", "loads/wind.py"),
        ("src\\loads\\wind.py", "loads/wind.py"),
    ],
)
def test_normalize_source_rel_path_strips_prefixes(raw: str, expected: str) -> None:
    assert normalize_source_rel_path(raw).as_posix() == expected


@pytest.mark.parametrize("bad", ["../escape.py", "src/../../escape.py", "notes.txt", "  "])
def test_normalize_source_rel_path_rejects_invalid(bad: str) -> None:
    with pytest.raises(PipelineError):
        normalize_source_rel_path(bad)


def test_call_with_retries_succeeds_after_transient_errors() -> None:
    calls = {"n": 0}
    slept = []

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise ValueError("transient")
        return "ok"

    result = call_with_retries(
        flaky, retries=3, base_delay=1, retryable=(ValueError,), sleep=slept.append
    )

    assert result == "ok"
    assert calls["n"] == 3
    assert slept == [1, 2]  # exponential backoff: 1*2^0, 1*2^1


def test_call_with_retries_does_not_retry_non_retryable() -> None:
    calls = {"n": 0}

    def boom():
        calls["n"] += 1
        raise KeyError("auth")

    with pytest.raises(KeyError):
        call_with_retries(
            boom, retries=3, base_delay=0, retryable=(ValueError,), sleep=lambda _d: None
        )

    assert calls["n"] == 1  # raised immediately, no retries


def test_call_with_retries_exhausts_and_raises_last() -> None:
    calls = {"n": 0}

    def always_fail():
        calls["n"] += 1
        raise ValueError(f"fail-{calls['n']}")

    with pytest.raises(ValueError):
        call_with_retries(
            always_fail, retries=2, base_delay=0, retryable=(ValueError,), sleep=lambda _d: None
        )

    assert calls["n"] == 3  # initial + 2 retries


def test_tables_to_markdown_renders_rows() -> None:
    from scripts.auto_codify import tables_to_markdown

    md, count = tables_to_markdown([[["回歸期\nn", "0.5", "1"], ["係數", "0.30", "0.46"]]])

    assert count == 1
    assert "[표 1]" in md
    assert "| 回歸期 n | 0.5 | 1 |" in md  # newline collapsed
    assert "| --- | --- | --- |" in md
    assert "| 係數 | 0.30 | 0.46 |" in md


def test_tables_to_markdown_handles_none_and_ragged_rows() -> None:
    from scripts.auto_codify import tables_to_markdown

    md, count = tables_to_markdown([[["a", None], ["b"]]])  # None cell + short row

    assert count == 1
    assert "| a |  |" in md
    assert "| b |  |" in md  # padded to width 2


def test_tables_to_markdown_escapes_pipe_and_backslash() -> None:
    """셀에 '|' 가 있으면 열 경계로 오인되어 표가 깨지므로 이스케이프해야 한다(#17 정확도)."""
    from scripts.auto_codify import tables_to_markdown

    md, count = tables_to_markdown([[["h", "unit"], ["a", "kN|m"], ["b", "x\\y"]]])

    assert count == 1
    assert "kN\\|m" in md  # 원본 파이프는 이스케이프되어 남아 있어야 함
    assert "x\\\\y" in md  # 백슬래시도 이스케이프
    assert "| a | kN\\|m |" in md  # 열이 3개로 밀리지 않고 2열 그대로 유지


def test_tables_to_markdown_empty() -> None:
    from scripts.auto_codify import tables_to_markdown

    assert tables_to_markdown([]) == ("", 0)
    assert tables_to_markdown([[[None, None]]]) == ("", 0)  # all-empty rows dropped


def test_tables_to_markdown_count_ignores_bracket_text_in_cells() -> None:
    """표 카운트는 렌더링된 블록 수 기준이라 셀 안의 '[표 ' 문자열에 오염되지 않는다(#regression)."""
    from scripts.auto_codify import tables_to_markdown

    md, count = tables_to_markdown(
        [[["ref", "note"], ["1", "[표 3] 참조"]]]
    )

    assert count == 1


def test_enforce_reference_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    import scripts.auto_codify as ac

    monkeypatch.setattr(ac, "MAX_REFERENCE_FILES", 2)
    ac.enforce_reference_limit([Path("a"), Path("b")])  # at limit: ok
    with pytest.raises(PipelineError):
        ac.enforce_reference_limit([Path("a"), Path("b"), Path("c")])


def test_enforce_file_size(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import scripts.auto_codify as ac

    f = tmp_path / "big.txt"
    f.write_bytes(b"x" * (3 * 1024 * 1024))  # 3 MB
    monkeypatch.setattr(ac, "MAX_FILE_MB", 1)
    with pytest.raises(PipelineError):
        ac.enforce_file_size(f)
    monkeypatch.setattr(ac, "MAX_FILE_MB", 10)
    ac.enforce_file_size(f)  # under limit: ok

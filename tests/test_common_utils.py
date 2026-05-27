from tools.common_utils import truncate_text


def test_truncate_text_returns_short_text_unchanged():
    assert truncate_text("short", 10, "sample") == "short"


def test_truncate_text_preserves_start_and_end_with_marker():
    text = "a" * 50 + "middle" + "z" * 50

    result = truncate_text(text, 60, "sample")

    assert len(result) <= 60
    assert result.startswith("a")
    assert result.endswith("z")
    assert "[TRUNCATED sample:" in result

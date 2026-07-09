"""Test chapter-mode output naming and overwrite logic from lib/core.py.

NOTE: _chapter_filename duplicates the inline f-string in
core.py's combined_audio_chapters(). If that pattern changes,
this test must be updated manually to match.
"""

import os


def _chapter_filename(stem: str, idx: int, total: int, fmt: str) -> str:
    """Duplicates the chapter filename f-string from combined_audio_chapters()."""
    pad = len(str(total))
    return f"{stem}_Ch{idx + 1:0{pad}d}.{fmt}"


class TestChapterNaming:
    """Chapter file naming: {stem}_Ch{idx:pad}.{format}."""

    def test_single_chapter(self):
        name = _chapter_filename("my_book", idx=0, total=1, fmt="m4b")
        assert name == "my_book_Ch1.m4b"

    def test_two_digit_padding(self):
        name_9 = _chapter_filename("book", idx=8, total=10, fmt="mp3")
        assert name_9 == "book_Ch09.mp3"
        name_10 = _chapter_filename("book", idx=9, total=10, fmt="mp3")
        assert name_10 == "book_Ch10.mp3"

    def test_three_digit_padding(self):
        name = _chapter_filename("book", idx=99, total=100, fmt="m4b")
        assert name == "book_Ch100.m4b"

    def test_all_chapters_unique(self):
        names = {_chapter_filename("b", i, 5, "m4b") for i in range(5)}
        assert len(names) == 5
        assert all(n.startswith("b_Ch") for n in names)

    def test_special_chars_in_stem(self):
        name = _chapter_filename("my book (v2)", idx=0, total=1, fmt="m4b")
        assert name == "my book (v2)_Ch1.m4b"


class TestOverwriteSkipLogic:
    """Simulates the skip-if-exists logic from chapter mode (lines 3583-3589)."""

    def _should_skip(self, chapter_path: str, overwrite: bool) -> bool:
        return (
            os.path.exists(chapter_path)
            and os.path.getsize(chapter_path) > 0
            and not overwrite
        )

    def test_skip_existing_no_overwrite(self, tmp_path):
        f = tmp_path / "chapter.m4b"
        f.write_text("fake audio data")
        assert self._should_skip(str(f), overwrite=False) is True

    def test_overwrite_True_does_not_skip(self, tmp_path):
        f = tmp_path / "chapter.m4b"
        f.write_text("fake audio data")
        assert self._should_skip(str(f), overwrite=True) is False

    def test_empty_file_not_skipped(self, tmp_path):
        f = tmp_path / "chapter.m4b"
        f.write_text("")  # empty
        assert self._should_skip(str(f), overwrite=False) is False

    def test_nonexistent_file_not_skipped(self, tmp_path):
        f = tmp_path / "nonexistent.m4b"
        assert self._should_skip(str(f), overwrite=False) is False

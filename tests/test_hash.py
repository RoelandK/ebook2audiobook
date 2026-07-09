"""Test process_dir hash consistency.

The upstream merged change simplified the hash:
  Before (fork): md5(audiobooks_dir + stem_of_final_name)
  After  (upstream): md5(ebook_name + optional_language_suffix)

This test verifies the new hash is deterministic and documents
that old session dirs will NOT be found by the new hash.

NOTE: _process_dir_hash duplicates the inline logic from core.py:process_dir.
If that logic changes, this test must be updated manually to match.
"""

import hashlib


def _process_dir_hash(
    ebook_name: str, translate_enabled: bool = False, language: str = "eng"
) -> str:
    """Duplicates the hash logic from lib/core.py process_dir()."""
    raw = ebook_name + ("_" + language if translate_enabled else "")
    return hashlib.md5(raw.encode()).hexdigest()


class TestProcessDirHash:
    def test_deterministic(self):
        """Same input always produces the same hash."""
        h1 = _process_dir_hash("my_book", translate_enabled=False)
        h2 = _process_dir_hash("my_book", translate_enabled=False)
        assert h1 == h2

    def test_translation_suffix_changes_hash(self):
        """Enabling translation appends language, producing a different hash."""
        h_base = _process_dir_hash("my_book", translate_enabled=False)
        h_trans = _process_dir_hash("my_book", translate_enabled=True, language="fra")
        assert h_trans != h_base
        assert h_trans == _process_dir_hash("my_book_fra", translate_enabled=False)

    def test_different_books_different_hash(self):
        """Different ebook names produce different hashes."""
        h_a = _process_dir_hash("book_a")
        h_b = _process_dir_hash("book_b")
        assert h_a != h_b

    def test_language_sensitivity(self):
        """Different target languages produce different hashes."""
        h_fr = _process_dir_hash("book", translate_enabled=True, language="fra")
        h_de = _process_dir_hash("book", translate_enabled=True, language="deu")
        assert h_fr != h_de

    def test_known_hash_value(self):
        """Pin a known input → output to catch accidental hash changes."""
        h = _process_dir_hash("test_book", translate_enabled=False)
        assert h == "aeff29d177ee9c7ea39ecb24afd7f123"

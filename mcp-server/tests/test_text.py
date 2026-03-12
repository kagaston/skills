"""Tests for text analysis and transformation tools."""

import pytest

from mcp_server.tools.text import analyze_text, hash_text, transform_text


class TestAnalyzeText:
    def test_basic_analysis(self):
        result = analyze_text("Hello world. This is a test.")
        assert result["words"] == 6
        assert result["sentences"] == 2
        assert result["characters"] > 0

    def test_paragraph_count(self):
        result = analyze_text("Paragraph one.\n\nParagraph two.")
        assert result["paragraphs"] == 2

    def test_top_words(self):
        result = analyze_text("the cat and the dog and the fish")
        top = dict(result["top_words"])
        assert top["the"] == 3
        assert top["and"] == 2

    def test_empty_text_raises(self):
        with pytest.raises(ValueError, match="empty"):
            analyze_text("   ")


class TestTransformText:
    def test_uppercase(self):
        assert transform_text("hello", "uppercase") == "HELLO"

    def test_lowercase(self):
        assert transform_text("HELLO", "lowercase") == "hello"

    def test_title(self):
        assert transform_text("hello world", "title") == "Hello World"

    def test_reverse(self):
        assert transform_text("abc", "reverse") == "cba"

    def test_sort_lines(self):
        assert transform_text("b\na\nc", "sort_lines") == "a\nb\nc"

    def test_deduplicate_lines(self):
        assert transform_text("a\nb\na\nc", "deduplicate_lines") == "a\nb\nc"

    def test_replace(self):
        assert transform_text("hello world", "replace", find="world", replace="there") == "hello there"

    def test_replace_missing_find_raises(self):
        with pytest.raises(ValueError, match="find"):
            transform_text("hello", "replace", find="", replace="x")

    def test_unknown_operation_raises(self):
        with pytest.raises(ValueError, match="Unknown operation"):
            transform_text("hello", "explode")


class TestHashText:
    def test_sha256(self):
        result = hash_text("hello", "sha256")
        assert result["algorithm"] == "sha256"
        assert len(result["digest"]) == 64

    def test_md5(self):
        result = hash_text("hello", "md5")
        assert result["algorithm"] == "md5"
        assert len(result["digest"]) == 32

    def test_unsupported_algorithm_raises(self):
        with pytest.raises(ValueError, match="Unsupported"):
            hash_text("hello", "blake2")

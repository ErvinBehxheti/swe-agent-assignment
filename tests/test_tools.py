"""
Unit tests for the three tools: calculator, file_reader, web_search.
No API key or network access is required for any of these tests.
"""

import csv
import os
import tempfile
from unittest.mock import MagicMock, patch

import pytest

from src.tools.calculator import calculate
from src.tools.file_reader import read_file
from src.tools.web_search import web_search


# ---------------------------------------------------------------------------
# Calculator
# ---------------------------------------------------------------------------

class TestCalculator:
    def test_addition(self):
        result = calculate("2 + 3")
        assert result["result"] == 5

    def test_subtraction(self):
        assert calculate("10 - 4")["result"] == 6

    def test_multiplication(self):
        assert calculate("6 * 7")["result"] == 42

    def test_division(self):
        assert calculate("10 / 4")["result"] == 2.5

    def test_floor_division(self):
        assert calculate("10 // 3")["result"] == 3

    def test_modulo(self):
        assert calculate("10 % 3")["result"] == 1

    def test_exponentiation(self):
        assert calculate("2 ** 8")["result"] == 256

    def test_sqrt(self):
        assert calculate("sqrt(144)")["result"] == 12.0

    def test_combined_expression(self):
        result = calculate("sqrt(1764) + 2**3")
        assert result["result"] == 50.0  # sqrt(1764)=42, 42+8=50

    def test_math_constants_pi(self):
        result = calculate("round(pi, 5)")
        assert result["result"] == 3.14159

    def test_nested_functions(self):
        result = calculate("round(sqrt(2), 4)")
        assert result["result"] == 1.4142

    def test_division_by_zero(self):
        result = calculate("1 / 0")
        assert "error" in result
        assert "zero" in result["error"].lower()

    def test_invalid_syntax(self):
        result = calculate("2 +* 3")
        assert "error" in result

    def test_code_injection_blocked(self):
        result = calculate("__import__('os').system('echo hi')")
        assert "error" in result

    def test_expression_stored_in_result(self):
        result = calculate("3 + 4")
        assert result["expression"] == "3 + 4"


# ---------------------------------------------------------------------------
# File Reader
# ---------------------------------------------------------------------------

class TestFileReader:
    def test_read_txt_file(self, tmp_path):
        f = tmp_path / "test.txt"
        f.write_text("Hello, World!", encoding="utf-8")
        result = read_file(str(f))
        assert result["content"] == "Hello, World!"
        assert result["type"] == "text"

    def test_read_md_file(self, tmp_path):
        f = tmp_path / "notes.md"
        f.write_text("# Title\nSome content.", encoding="utf-8")
        result = read_file(str(f))
        assert "Title" in result["content"]
        assert result["type"] == "text"

    def test_read_csv_file(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_text("Name,Score\nAlice,95\nBob,80\n", encoding="utf-8")
        result = read_file(str(f))
        assert result["type"] == "csv"
        assert "Alice" in result["content"]
        assert "Bob" in result["content"]
        assert result["rows"] == 2

    def test_file_not_found(self):
        result = read_file("/nonexistent/path/file.txt")
        assert "error" in result
        assert "not found" in result["error"].lower()

    def test_unsupported_extension(self, tmp_path):
        f = tmp_path / "script.py"
        f.write_text("print('hi')", encoding="utf-8")
        result = read_file(str(f))
        assert "error" in result
        assert "Unsupported" in result["error"]

    def test_empty_csv(self, tmp_path):
        f = tmp_path / "empty.csv"
        f.write_text("", encoding="utf-8")
        result = read_file(str(f))
        assert result["type"] == "csv"
        assert "empty" in result["content"].lower()

    def test_file_path_returned(self, tmp_path):
        f = tmp_path / "hello.txt"
        f.write_text("data", encoding="utf-8")
        result = read_file(str(f))
        assert "file" in result

    def test_file_too_large(self, tmp_path, monkeypatch):
        # Patch the size limit to 10 bytes so we don't create a huge file
        import src.tools.file_reader as fr_module
        monkeypatch.setattr(fr_module, "MAX_FILE_SIZE_BYTES", 10)
        f = tmp_path / "big.txt"
        f.write_text("x" * 100, encoding="utf-8")
        result = read_file(str(f))
        assert "error" in result
        assert "size limit" in result["error"].lower()


# ---------------------------------------------------------------------------
# Web Search
# ---------------------------------------------------------------------------

class TestWebSearch:
    def _make_ddgs_hit(self, title="Test Title", href="https://example.com", body="A snippet."):
        return {"title": title, "href": href, "body": body}

    def test_returns_results(self):
        mock_hits = [self._make_ddgs_hit(title=f"Result {i}") for i in range(3)]
        with patch("src.tools.web_search.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = mock_hits
            result = web_search("Python programming")
        assert "results" in result
        assert len(result["results"]) == 3
        assert result["results"][0]["title"] == "Result 0"

    def test_result_structure(self):
        mock_hits = [self._make_ddgs_hit()]
        with patch("src.tools.web_search.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = mock_hits
            result = web_search("anything")
        r = result["results"][0]
        assert "title" in r
        assert "url" in r
        assert "snippet" in r

    def test_empty_query(self):
        result = web_search("   ")
        assert "error" in result

    def test_no_results(self):
        with patch("src.tools.web_search.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = []
            result = web_search("xkcd obscure query 12345")
        assert result["results"] == []
        assert "message" in result

    def test_network_error(self):
        with patch("src.tools.web_search.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.side_effect = Exception("Connection refused")
            result = web_search("test query")
        assert "error" in result
        assert "Connection refused" in result["error"]

    def test_query_stored_in_result(self):
        with patch("src.tools.web_search.DDGS") as MockDDGS:
            instance = MockDDGS.return_value.__enter__.return_value
            instance.text.return_value = []
            result = web_search("my query")
        assert result["query"] == "my query"

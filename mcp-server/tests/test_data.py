"""Tests for data processing and calculation tools."""

import pytest

from mcp_server.tools.data import calculate, json_query, parse_csv, statistics_summary


class TestCalculate:
    def test_basic_arithmetic(self):
        assert calculate("2 + 3")["result"] == 5.0

    def test_power(self):
        assert calculate("2 ** 10")["result"] == 1024.0

    def test_sqrt(self):
        assert calculate("sqrt(144)")["result"] == 12.0

    def test_pi(self):
        result = calculate("round(pi, 2)")
        assert result["result"] == 3.14

    def test_empty_expression_raises(self):
        with pytest.raises(ValueError, match="empty"):
            calculate("   ")

    def test_invalid_expression_raises(self):
        with pytest.raises(ValueError, match="Invalid expression"):
            calculate("import os")


class TestStatisticsSummary:
    def test_basic_stats(self):
        result = statistics_summary([1, 2, 3, 4, 5])
        assert result["count"] == 5
        assert result["mean"] == 3.0
        assert result["median"] == 3
        assert result["sum"] == 15
        assert result["min"] == 1
        assert result["max"] == 5

    def test_stdev_present_for_multiple_values(self):
        result = statistics_summary([1.0, 2.0, 3.0])
        assert "stdev" in result

    def test_stdev_absent_for_single_value(self):
        result = statistics_summary([42.0])
        assert "stdev" not in result

    def test_empty_list_raises(self):
        with pytest.raises(ValueError, match="empty"):
            statistics_summary([])


class TestParseCsv:
    def test_basic_csv(self):
        rows = parse_csv("name,age\nAlice,30\nBob,25")
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"
        assert rows[1]["age"] == "25"

    def test_custom_delimiter(self):
        rows = parse_csv("name;age\nAlice;30", delimiter=";")
        assert rows[0]["name"] == "Alice"

    def test_empty_csv_raises(self):
        with pytest.raises(ValueError, match="empty"):
            parse_csv("")

    def test_headers_only_raises(self):
        with pytest.raises(ValueError, match="no data rows"):
            parse_csv("name,age\n")


class TestJsonQuery:
    def test_simple_key(self):
        assert json_query('{"name": "Alice"}', "name") == "Alice"

    def test_nested_key(self):
        assert json_query('{"user": {"name": "Bob"}}', "user.name") == "Bob"

    def test_array_index(self):
        assert json_query('{"items": [10, 20, 30]}', "items.1") == 20

    def test_invalid_json_raises(self):
        with pytest.raises(ValueError, match="Invalid JSON"):
            json_query("{bad", "key")

    def test_missing_key_raises(self):
        with pytest.raises(ValueError, match="not found"):
            json_query('{"a": 1}', "b")

    def test_invalid_array_index_raises(self):
        with pytest.raises(ValueError, match="Invalid array index"):
            json_query("[1, 2]", "5")

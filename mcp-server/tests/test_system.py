"""Tests for system information tools."""

from pathlib import Path

import pytest

from mcp_server.tools.system import get_system_info, list_directory, read_file_summary


class TestGetSystemInfo:
    def test_returns_expected_keys(self):
        info = get_system_info()
        expected = {"hostname", "os", "python_version", "cpu_count", "disk_total_gb", "utc_time"}
        assert expected.issubset(info.keys())

    def test_cpu_count_positive(self):
        assert get_system_info()["cpu_count"] >= 0


class TestListDirectory:
    def test_list_temp_dir(self, tmp_path: Path):
        (tmp_path / "file.txt").write_text("hello")
        (tmp_path / "sub").mkdir()
        entries = list_directory(str(tmp_path))
        names = {e["name"] for e in entries}
        assert "file.txt" in names
        assert "sub" in names

    def test_glob_pattern(self, tmp_path: Path):
        (tmp_path / "a.py").write_text("")
        (tmp_path / "b.txt").write_text("")
        entries = list_directory(str(tmp_path), pattern="*.py")
        assert len(entries) == 1
        assert entries[0]["name"] == "a.py"

    def test_hidden_files_excluded_by_default(self, tmp_path: Path):
        (tmp_path / ".hidden").write_text("")
        (tmp_path / "visible").write_text("")
        entries = list_directory(str(tmp_path))
        names = {e["name"] for e in entries}
        assert "visible" in names
        assert ".hidden" not in names

    def test_hidden_files_included(self, tmp_path: Path):
        (tmp_path / ".hidden").write_text("")
        entries = list_directory(str(tmp_path), include_hidden=True)
        names = {e["name"] for e in entries}
        assert ".hidden" in names

    def test_nonexistent_path_raises(self):
        with pytest.raises(FileNotFoundError):
            list_directory("/nonexistent/path/xyz")


class TestReadFileSummary:
    def test_reads_file(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("line1\nline2\nline3")
        result = read_file_summary(str(f))
        assert result["total_lines"] == 3
        assert not result["truncated"]

    def test_truncates(self, tmp_path: Path):
        f = tmp_path / "big.txt"
        f.write_text("\n".join(f"line {i}" for i in range(200)))
        result = read_file_summary(str(f), max_lines=10)
        assert result["truncated"]
        assert result["preview_lines"] == 10

    def test_nonexistent_file_raises(self):
        with pytest.raises(FileNotFoundError):
            read_file_summary("/no/such/file.txt")

    def test_directory_raises(self, tmp_path: Path):
        with pytest.raises(IsADirectoryError):
            read_file_summary(str(tmp_path))

    def test_invalid_max_lines_raises(self, tmp_path: Path):
        f = tmp_path / "test.txt"
        f.write_text("hello")
        with pytest.raises(ValueError, match="positive"):
            read_file_summary(str(f), max_lines=0)

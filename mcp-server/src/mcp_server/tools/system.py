"""System information tools for the MCP server."""

import os
import platform
import shutil
from datetime import UTC, datetime
from pathlib import Path


def get_system_info() -> dict[str, str | int | float]:
    """Retrieve detailed system information.

    Returns host, OS, architecture, Python version, CPU count,
    and disk usage for the root filesystem.
    """
    disk = shutil.disk_usage("/")
    return {
        "hostname": platform.node(),
        "os": platform.system(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "cpu_count": os.cpu_count() or 0,
        "disk_total_gb": round(disk.total / (1024**3), 2),
        "disk_free_gb": round(disk.free / (1024**3), 2),
        "disk_used_percent": round((disk.used / disk.total) * 100, 1),
        "utc_time": datetime.now(UTC).isoformat(),
    }


def list_directory(path: str, pattern: str = "*", include_hidden: bool = False) -> list[dict[str, str | int]]:
    """List files and directories at the given path.

    Args:
        path: Directory path to list.
        pattern: Glob pattern to filter entries (e.g. '*.py').
        include_hidden: Whether to include dotfiles/dotdirs.

    Returns:
        List of entries with name, type, and size.

    Raises:
        FileNotFoundError: If the path does not exist.
        NotADirectoryError: If the path is not a directory.
    """
    target = Path(path).expanduser().resolve()
    if not target.exists():
        raise FileNotFoundError(f"Path does not exist: {target}")
    if not target.is_dir():
        raise NotADirectoryError(f"Not a directory: {target}")

    entries: list[dict[str, str | int]] = []
    for item in sorted(target.glob(pattern)):
        if not include_hidden and item.name.startswith("."):
            continue
        entry: dict[str, str | int] = {
            "name": item.name,
            "type": "directory" if item.is_dir() else "file",
        }
        if item.is_file():
            entry["size_bytes"] = item.stat().st_size
        entries.append(entry)
    return entries


def read_file_summary(path: str, max_lines: int = 50) -> dict[str, str | int]:
    """Read a file and return its metadata plus a content preview.

    Args:
        path: Path to the file.
        max_lines: Maximum number of lines to include in the preview.

    Returns:
        Dict with file metadata and content preview.

    Raises:
        FileNotFoundError: If the file does not exist.
        IsADirectoryError: If the path is a directory.
        ValueError: If max_lines is not positive.
    """
    if max_lines <= 0:
        raise ValueError("max_lines must be positive")

    target = Path(path).expanduser().resolve()
    if not target.exists():
        raise FileNotFoundError(f"File does not exist: {target}")
    if target.is_dir():
        raise IsADirectoryError(f"Path is a directory: {target}")

    stat = target.stat()
    try:
        content = target.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return {
            "path": str(target),
            "size_bytes": stat.st_size,
            "content": "[binary file - cannot display]",
            "total_lines": 0,
            "truncated": False,
        }

    lines = content.splitlines()
    total = len(lines)
    preview = "\n".join(lines[:max_lines])
    return {
        "path": str(target),
        "size_bytes": stat.st_size,
        "total_lines": total,
        "preview_lines": min(total, max_lines),
        "truncated": total > max_lines,
        "content": preview,
    }

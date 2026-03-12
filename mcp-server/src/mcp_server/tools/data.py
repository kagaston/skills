"""Data processing and calculation tools."""

import contextlib
import csv
import io
import json
import math
import statistics
from typing import Any

_MIN_FOR_STDEV = 2


def calculate(expression: str) -> dict[str, str | float]:
    """Evaluate a mathematical expression safely.

    Supports basic arithmetic, power, sqrt, abs, round, min, max,
    pi, e, and trigonometric functions.

    Args:
        expression: Mathematical expression to evaluate (e.g. 'sqrt(144) + 2**3').

    Returns:
        Dict with the expression and its result.

    Raises:
        ValueError: If the expression is empty or contains disallowed constructs.
    """
    if not expression.strip():
        raise ValueError("Expression cannot be empty")

    safe_names: dict[str, Any] = {
        "abs": abs,
        "round": round,
        "min": min,
        "max": max,
        "sqrt": math.sqrt,
        "pow": pow,
        "log": math.log,
        "log10": math.log10,
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "pi": math.pi,
        "e": math.e,
        "ceil": math.ceil,
        "floor": math.floor,
    }

    try:
        result = eval(expression, {"__builtins__": {}}, safe_names)  # noqa: S307
    except Exception as exc:
        raise ValueError(f"Invalid expression: {exc}") from exc

    return {"expression": expression, "result": float(result)}


def statistics_summary(numbers: list[float]) -> dict[str, float | int]:
    """Compute descriptive statistics for a list of numbers.

    Args:
        numbers: List of numeric values.

    Returns:
        Dict with count, mean, median, mode, stdev, min, max, and sum.

    Raises:
        ValueError: If the list is empty.
    """
    if not numbers:
        raise ValueError("Numbers list cannot be empty")

    result: dict[str, float | int] = {
        "count": len(numbers),
        "sum": sum(numbers),
        "mean": round(statistics.mean(numbers), 6),
        "median": statistics.median(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }

    if len(numbers) >= _MIN_FOR_STDEV:
        result["stdev"] = round(statistics.stdev(numbers), 6)
        result["variance"] = round(statistics.variance(numbers), 6)

    with contextlib.suppress(statistics.StatisticsError):
        result["mode"] = statistics.mode(numbers)

    return result


def parse_csv(csv_text: str, delimiter: str = ",") -> list[dict[str, str]]:
    """Parse CSV text into a list of dictionaries.

    The first row is treated as headers.

    Args:
        csv_text: Raw CSV content as a string.
        delimiter: Column delimiter character.

    Returns:
        List of row dictionaries keyed by header names.

    Raises:
        ValueError: If the CSV text is empty or has no data rows.
    """
    if not csv_text.strip():
        raise ValueError("CSV text cannot be empty")

    reader = csv.DictReader(io.StringIO(csv_text), delimiter=delimiter)
    rows = list(reader)
    if not rows:
        raise ValueError("CSV contains headers but no data rows")
    return rows


def json_query(json_text: str, path: str) -> Any:
    """Extract a value from JSON using a dot-notation path.

    Supports nested keys and integer array indices.

    Args:
        json_text: Raw JSON string.
        path: Dot-separated path (e.g. 'users.0.name').

    Returns:
        The value at the specified path.

    Raises:
        ValueError: If JSON is invalid or path does not exist.
    """
    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON: {exc}") from exc

    current: Any = data
    for key in path.split("."):
        if isinstance(current, list):
            try:
                current = current[int(key)]
            except (ValueError, IndexError) as exc:
                raise ValueError(f"Invalid array index '{key}' in path '{path}'") from exc
        elif isinstance(current, dict):
            if key not in current:
                raise ValueError(f"Key '{key}' not found at path '{path}'")
            current = current[key]
        else:
            raise ValueError(f"Cannot traverse into {type(current).__name__} with key '{key}'")

    return current

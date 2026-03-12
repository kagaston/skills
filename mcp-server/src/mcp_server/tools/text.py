"""Text analysis and transformation tools."""

import hashlib
import re
from collections import Counter


def analyze_text(text: str) -> dict[str, int | float | list[tuple[str, int]]]:
    """Analyze text and return statistics.

    Returns character count, word count, sentence count, paragraph count,
    average word length, and the 10 most common words.

    Args:
        text: The text to analyze.

    Returns:
        Dictionary of text statistics.

    Raises:
        ValueError: If text is empty.
    """
    if not text.strip():
        raise ValueError("Text cannot be empty")

    words = re.findall(r"\b\w+\b", text.lower())
    sentences = re.split(r"[.!?]+", text)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    word_freq = Counter(words).most_common(10)
    avg_word_len = sum(len(w) for w in words) / len(words) if words else 0.0

    return {
        "characters": len(text),
        "characters_no_spaces": len(text.replace(" ", "")),
        "words": len(words),
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "avg_word_length": round(avg_word_len, 2),
        "top_words": word_freq,
    }


def transform_text(
    text: str,
    operation: str,
    find: str = "",
    replace: str = "",
) -> str:
    """Transform text using the specified operation.

    Args:
        text: Input text to transform.
        operation: One of 'uppercase', 'lowercase', 'title', 'reverse',
                   'strip', 'deduplicate_lines', 'sort_lines', 'replace'.
        find: String to find (required for 'replace' operation).
        replace: Replacement string (used with 'replace' operation).

    Returns:
        The transformed text.

    Raises:
        ValueError: If operation is unknown or find is empty for replace.
    """
    ops: dict[str, object] = {
        "uppercase": lambda: text.upper(),
        "lowercase": lambda: text.lower(),
        "title": lambda: text.title(),
        "reverse": lambda: text[::-1],
        "strip": lambda: "\n".join(line.strip() for line in text.splitlines()),
        "deduplicate_lines": lambda: "\n".join(dict.fromkeys(text.splitlines())),
        "sort_lines": lambda: "\n".join(sorted(text.splitlines())),
        "replace": lambda: _do_replace(text, find, replace),
    }

    if operation not in ops:
        raise ValueError(f"Unknown operation '{operation}'. Valid: {', '.join(ops)}")

    fn = ops[operation]
    return fn()  # type: ignore[operator]


def _do_replace(text: str, find: str, replace: str) -> str:
    if not find:
        raise ValueError("'find' parameter is required for replace operation")
    return text.replace(find, replace)


def hash_text(text: str, algorithm: str = "sha256") -> dict[str, str]:
    """Compute a cryptographic hash of the given text.

    Args:
        text: Text to hash.
        algorithm: Hash algorithm ('md5', 'sha1', 'sha256', 'sha512').

    Returns:
        Dict with algorithm name and hex digest.

    Raises:
        ValueError: If algorithm is not supported.
    """
    supported = {"md5", "sha1", "sha256", "sha512"}
    if algorithm not in supported:
        raise ValueError(f"Unsupported algorithm '{algorithm}'. Valid: {', '.join(sorted(supported))}")

    h = hashlib.new(algorithm, text.encode("utf-8"))
    return {"algorithm": algorithm, "digest": h.hexdigest()}

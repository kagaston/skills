---
name: bash-cross-platform
description: Writing Bash scripts that work on both macOS and Linux, including Bash 3.2 compatibility constraints, BSD vs GNU command differences, and platform detection wrappers. Use when writing cross-platform shell scripts, targeting macOS compatibility, or dealing with stat/date/sha256 differences between macOS and Linux.
---

# Bash Cross-Platform

Write Bash scripts that run correctly on both macOS (BSD userland, Bash 3.2) and Linux (GNU userland, Bash 5+). macOS ships with Bash 3.2 due to licensing -- many modern Bash features silently fail or produce wrong results on it.

## Bash 3.2 Constraints

macOS ships Bash 3.2 by default. If your script needs to work on stock macOS, avoid these features entirely.

### Banned Features

| Feature | Bash version | What to use instead |
|---------|-------------|---------------------|
| Associative arrays (`declare -A`) | 4.0+ | `case` function as lookup table |
| `${var,,}` lowercase | 4.0+ | `echo "$var" \| tr '[:upper:]' '[:lower:]'` |
| `${var^^}` uppercase | 4.0+ | `echo "$var" \| tr '[:lower:]' '[:upper:]'` |
| Nameref variables (`declare -n`) | 4.3+ | Pass variable name as string, use `eval` carefully |
| `readarray` / `mapfile` | 4.0+ | `while IFS= read -r` loop |
| `${var@Q}` quoting | 4.4+ | `printf '%q'` |
| `{1..N}` where N is a variable | All | `seq 1 "$n"` |
| `\|&` (pipe stderr+stdout) | 4.0+ | `2>&1 \|` |
| `coproc` | 4.0+ | Named pipes or temp files |

### Associative Array Alternative

Use `case` functions as lookup tables instead of associative arrays:

```bash
# Instead of: declare -A severity=([critical]=4 [high]=3 [medium]=2 [low]=1)
_severity_weight() {
    case "$1" in
        critical) echo 4 ;;
        high)     echo 3 ;;
        medium)   echo 2 ;;
        low)      echo 1 ;;
        *)        echo 0 ;;
    esac
}

weight="$(_severity_weight "$level")"
```

### Lowercase/Uppercase Alternative

```bash
# Instead of: lower="${var,,}"
lower="$(echo "$var" | tr '[:upper:]' '[:lower:]')"

# Instead of: upper="${var^^}"
upper="$(echo "$var" | tr '[:lower:]' '[:upper:]')"
```

## BSD vs GNU Command Differences

macOS uses BSD userland; Linux uses GNU coreutils. Many commands share names but have incompatible flags. Centralise these differences into platform wrapper functions rather than scattering `if/else` throughout the codebase.

### Platform Detection

Detect once at load time so every subsequent call is a cheap string comparison:

```bash
PLATFORM="$(uname -s)"

is_linux()  { [[ "$PLATFORM" == "Linux" ]]; }
is_darwin() { [[ "$PLATFORM" == "Darwin" ]]; }

has_cmd() { command -v "$1" &>/dev/null; }
```

### stat

The most common divergence. GNU uses `-c` for format; BSD uses `-f`.

```bash
file_size() {
    if is_linux; then
        stat -c '%s' "$1" 2>/dev/null
    else
        stat -f '%z' "$1" 2>/dev/null
    fi
}

file_mtime() {
    if is_linux; then
        stat -c '%Y' "$1" 2>/dev/null
    else
        stat -f '%m' "$1" 2>/dev/null
    fi
}

file_perms() {
    if is_linux; then
        stat -c '%a' "$1" 2>/dev/null
    else
        stat -f '%Lp' "$1" 2>/dev/null
    fi
}
```

### date

Epoch-to-ISO conversion differs:

```bash
epoch_to_iso() {
    if is_linux; then
        date -u -d "@${1}" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null
    else
        date -u -r "${1}" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null
    fi
}

# These are consistent across platforms
utc_now()   { date -u '+%Y-%m-%dT%H:%M:%SZ'; }
epoch_now() { date +%s; }
```

### Hashing

```bash
compute_sha256() {
    if is_linux; then
        sha256sum "$1" 2>/dev/null | awk '{print $1}'
    else
        shasum -a 256 "$1" 2>/dev/null | awk '{print $1}'
    fi
}

compute_md5() {
    if is_linux; then
        md5sum "$1" 2>/dev/null | awk '{print $1}'
    else
        md5 -q "$1" 2>/dev/null
    fi
}
```

### sed

GNU sed uses `-i ''` differently from BSD sed:

```bash
# GNU: sed -i 's/old/new/' file
# BSD: sed -i '' 's/old/new/' file
sed_inplace() {
    if is_linux; then
        sed -i "$@"
    else
        sed -i '' "$@"
    fi
}
```

### Package Manager Detection

```bash
detect_pkg_manager() {
    if is_darwin; then
        echo "brew"
    elif has_cmd dpkg; then
        echo "dpkg"
    elif has_cmd rpm; then
        echo "rpm"
    else
        echo "unknown"
    fi
}
```

## Include Guards

Prevent double-sourcing when multiple modules depend on the same file:

```bash
_MODULE_LOADED=${_MODULE_LOADED:-false}
[[ "$_MODULE_LOADED" == "true" ]] && return 0
_MODULE_LOADED=true
```

Use string comparison ("true"/"false") rather than integer flags for clarity and compatibility with `set -u` (undefined variable checks).

## Optional Dependency Pattern

Check for optional tools at runtime and provide fallbacks:

```bash
if has_cmd jq; then
    printf '%s' "$json" | jq '.' > "$output"
else
    printf '%s\n' "$json" > "$output"
fi
```

Group optional dependency checks at startup and report what's available:

```bash
log_info "Optional tools: jq=$(has_cmd jq && echo yes || echo no), yara=$(has_cmd yara && echo yes || echo no)"
```

## Testing Cross-Platform Scripts

- Test on macOS (BSD `sed`, `stat`, `date`, Bash 3.2) and Linux (GNU equivalents, Bash 5+)
- Use `has_cmd` before any platform-specific command
- Suppress stderr on platform wrappers (`2>/dev/null`) so callers get clean empty strings on failure
- Use `shellcheck -x` to catch cross-platform issues in sourced files

## Verification Checklist

- [ ] No Bash 4+ features used (associative arrays, `${var,,}`, nameref, readarray)
- [ ] Platform wrappers for stat, date, hash, sed differences
- [ ] `has_cmd` checks before optional/platform-specific tools
- [ ] Include guards on all sourced modules
- [ ] Tested on both macOS and Linux
- [ ] `shellcheck` passes

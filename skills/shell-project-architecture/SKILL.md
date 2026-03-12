---
name: shell-project-architecture
description: Architecture patterns for multi-module shell projects including convention-based dispatch, pipeline orchestration, profile-driven configuration, pure-bash JSON generation, and auto-discovery. Use when building a large shell project with multiple scripts, creating a plugin/module system in bash, or structuring a shell-based tool.
argument-hint: "[project-name]"
---

# Shell Project Architecture

Patterns for building large, maintainable shell projects that go beyond single scripts. These patterns are extracted from production DFIR tools and CLI frameworks that manage 30+ shell modules.

## Project Layout

Organise shell projects by architectural role, not by file type:

```
project-name/
├── project-name.sh              # CLI entry point — arg parsing + dispatch
├── lib/
│   ├── engine.sh                # Pipeline orchestrator — sources + coordinates
│   ├── core/                    # Foundation modules (no business logic)
│   │   ├── config.sh            # Constants, signatures, lookup tables
│   │   ├── json.sh              # JSON construction helpers
│   │   ├── logging.sh           # Colored logging, audit trail
│   │   ├── platform.sh          # OS detection, cross-platform wrappers
│   │   └── utils.sh             # General utilities
│   ├── collectors/              # Input modules (one per data source)
│   ├── analyzers/               # Processing modules (one per analysis type)
│   ├── reporters/               # Output modules (one per format)
│   └── evidence/                # Integrity and chain-of-custody
├── profiles/                    # Configuration profiles
├── rules/                       # Detection/validation rules
├── justfile                     # Task runner
└── README.md
```

The key principle: each directory has a clear role, and modules within it follow a naming convention that enables auto-discovery.

## Convention-Based Dispatch

Name functions using a predictable pattern so the engine can discover and invoke them dynamically. This eliminates manual registration for new modules.

### The Pattern

```bash
# Convention: collect_<name>() in lib/collectors/<name>.sh
# Convention: report_<format>() in lib/reporters/<format>_reporter.sh
# Convention: analyze_<name>() in lib/analyzers/<name>.sh
```

### Auto-Discovery via Glob Sourcing

Source all modules from a directory at startup:

```bash
for _file in "${SCRIPT_DIR}"/lib/collectors/*.sh; do
    [[ -f "$_file" ]] && source "$_file"
done
```

The `[[ -f ]]` guard handles the edge case where a glob expands to a literal string (no matching files).

### Dynamic Dispatch

Resolve a name to a function at runtime:

```bash
run_collectors() {
    local output_dir="$1"
    for name in "${PROFILE_COLLECTORS[@]}"; do
        local func="collect_${name}"
        if declare -f "$func" &>/dev/null; then
            log_info "Running collector: ${name}"
            "$func" "$output_dir"
        else
            log_warn "Collector not found: ${name}"
        fi
    done
}
```

`declare -f` checks if the function exists before calling it -- this gives a clean warning instead of a crash when a profile references a collector that hasn't been implemented yet.

## Pipeline Orchestration

Structure multi-phase workflows as explicit pipeline stages:

```
Input → Collection → Analysis → Reporting → Output
```

```bash
engine_triage() {
    local output_dir="$1"

    mkdir -p "${output_dir}/raw" "${output_dir}/analysis"

    # Phase 1: Collect
    run_collectors "$output_dir"
    seal_evidence "$output_dir"

    # Phase 2: Analyze
    run_analyzers "$output_dir"

    # Phase 3: Report
    run_reporters "$output_dir"

    log_info "Pipeline complete: ${output_dir}"
}
```

Each phase reads from and writes to well-defined directories (`raw/`, `analysis/`), making the pipeline debuggable -- you can inspect intermediate state between phases.

## Profile-Driven Configuration

Use profile files to control which modules run without changing code:

```bash
# profiles/quick.conf
PROFILE_NAME="quick"
PROFILE_DESCRIPTION="Fast triage — 5 collectors, ~30 seconds"
PROFILE_COLLECTORS=(system_info processes network users persistence)
PROFILE_HASH_FILES=false
PROFILE_YARA_SCAN=false
```

```bash
# profiles/full.conf
PROFILE_NAME="full"
PROFILE_DESCRIPTION="Complete triage — all collectors + YARA + hashing"
PROFILE_COLLECTORS=(system_info processes network users persistence
    filesystem logs browser shell_history usb_devices installed_software
    kernel_modules firewall environment clipboard certificates)
PROFILE_HASH_FILES=true
PROFILE_YARA_SCAN=true
```

Load profiles by sourcing them:

```bash
load_profile() {
    local profile_file="${SCRIPT_DIR}/profiles/${1}.conf"
    [[ -f "$profile_file" ]] || { log_error "Profile not found: $1"; exit 1; }
    source "$profile_file"
}
```

## Module Template

Every module follows the same structure:

```bash
#!/usr/bin/env bash
# =============================================================================
# module_name.sh — Brief Description
# =============================================================================
#
# PURPOSE: What this module does.
# ARCHITECTURE ROLE: Where it fits in the pipeline.
# PLATFORM: macOS, Linux, or both.
#
# =============================================================================

# Include guard
_MODULE_LOADED=${_MODULE_LOADED:-false}
[[ "$_MODULE_LOADED" == "true" ]] && return 0
_MODULE_LOADED=true

# Dependencies (source guards prevent double-loading)
source "${SCRIPT_DIR}/lib/core/utils.sh"

# -----------------------------------------------------------------------------
# function_name — Brief description
#
# Parameters:
#   $1  param_name — description
#
# Returns: description of output
# -----------------------------------------------------------------------------
function_name() {
    local param="$1"
    # implementation
}
```

The header comment block uses `# ===` delimiters for the file header and `# ---` delimiters for individual functions. Comments explain *why*, not *what*.

## Pure-Bash JSON Generation

Build valid JSON without external dependencies using composable helper functions:

```bash
json_escape() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

json_kvs() { printf '"%s": "%s"' "$(json_escape "$1")" "$(json_escape "$2")"; }
json_kvn() { printf '"%s": %s' "$(json_escape "$1")" "$2"; }

json_object() {
    local result="{" first=true
    for pair in "$@"; do
        [[ "$first" == "true" ]] && first=false || result+=", "
        result+="$pair"
    done
    printf '%s' "${result}}"
}

json_array() {
    local result="[" first=true
    for elem in "$@"; do
        [[ "$first" == "true" ]] && first=false || result+=", "
        result+="$elem"
    done
    printf '%s' "${result}]"
}
```

Usage:

```bash
result="$(json_object \
    "$(json_kvs "hostname" "$hostname")" \
    "$(json_kvn "uptime" "$uptime_secs")" \
    "$(json_kvs "platform" "$PLATFORM")"
)"
json_write "$output_dir/raw/system_info.json" "$result"
```

For bulk data (hundreds+ items), use `awk` for JSON generation instead of per-item shell function calls to avoid subprocess overhead.

## Adding a New Module

### Collector

1. Create `lib/collectors/my_collector.sh`
2. Define `collect_my_collector()` taking `$1` = output_dir
3. Add `"my_collector"` to profile arrays in `profiles/*.conf`
4. Auto-discovered -- no registration code needed

### Analyzer

1. Create `lib/analyzers/my_analyzer.sh`
2. Define `analyze_my_analyzer()` taking `$1` = output_dir
3. Add the call to `run_analyzers()` in engine.sh (analyzers run in explicit order)

### Reporter

1. Create `lib/reporters/my_format_reporter.sh`
2. Define `report_my_format()` taking `$1` = output_dir
3. Auto-discovered when format is requested via CLI flag

## justfile for Shell Projects

```just
default:
    @just --list

lint:
    @find . -name '*.sh' -not -path './output/*' | while read f; do \
        bash -n "$$f" 2>&1 && echo "  OK: $$f" || echo "  FAIL: $$f"; \
    done

shellcheck:
    @find . -name '*.sh' -not -path './output/*' -exec shellcheck -x {} +

loc:
    @find . -name '*.sh' -not -path './output/*' | xargs wc -l | tail -1

list-modules:
    @grep -rh '^collect_\|^analyze_\|^report_' lib/ | sed 's/() {//' | sort
```

## Verification Checklist

- [ ] Modules follow naming convention (`collect_<name>`, `analyze_<name>`, `report_<format>`)
- [ ] Include guards on every sourced module
- [ ] Auto-discovery via glob sourcing with `[[ -f ]]` guard
- [ ] Pipeline phases write to well-defined directories
- [ ] Profile files control module selection without code changes
- [ ] File headers document purpose, architecture role, and platform support
- [ ] Function headers document parameters and return values
- [ ] `just lint` and `just shellcheck` pass

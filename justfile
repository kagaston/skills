set dotenv-load := false

goose_dir := env("HOME") / ".config/goose/skills"
cursor_dir := env("HOME") / ".cursor/skills"
skills_src := justfile_directory() / "skills"

default:
    @just --list

# Deploy all skills to Goose and Cursor locations via symlinks
deploy:
    #!/usr/bin/env bash
    set -euo pipefail
    goose_dir="{{goose_dir}}"
    cursor_dir="{{cursor_dir}}"
    src="{{skills_src}}"

    mkdir -p "$goose_dir" "$cursor_dir"

    for skill_dir in "$src"/*/; do
        skill_name=$(basename "$skill_dir")
        if [ ! -f "$skill_dir/SKILL.md" ]; then
            echo "SKIP $skill_name (no SKILL.md)"
            continue
        fi

        # Goose
        rm -rf "$goose_dir/$skill_name"
        ln -sf "$skill_dir" "$goose_dir/$skill_name"

        # Cursor
        rm -rf "$cursor_dir/$skill_name"
        ln -sf "$skill_dir" "$cursor_dir/$skill_name"

        echo "  OK $skill_name"
    done
    echo ""
    echo "Deployed to:"
    echo "  Goose  → $goose_dir"
    echo "  Cursor → $cursor_dir"

# List all available skills
list:
    #!/usr/bin/env bash
    set -euo pipefail
    printf "%-35s %s\n" "SKILL" "DESCRIPTION"
    printf "%-35s %s\n" "-----" "-----------"
    for skill_dir in "{{skills_src}}"/*/; do
        skill_name=$(basename "$skill_dir")
        if [ -f "$skill_dir/SKILL.md" ]; then
            desc=$(grep '^description:' "$skill_dir/SKILL.md" | head -1 | sed 's/^description: *//')
            printf "%-35s %s\n" "$skill_name" "$desc"
        fi
    done

# Validate all SKILL.md files have required frontmatter
validate:
    #!/usr/bin/env bash
    set -euo pipefail
    errors=0
    for skill_dir in "{{skills_src}}"/*/; do
        skill_name=$(basename "$skill_dir")
        file="$skill_dir/SKILL.md"
        if [ ! -f "$file" ]; then
            echo "FAIL $skill_name: missing SKILL.md"
            errors=$((errors + 1))
            continue
        fi
        if ! head -1 "$file" | grep -q '^---$'; then
            echo "FAIL $skill_name: missing frontmatter delimiter"
            errors=$((errors + 1))
            continue
        fi
        if ! grep -q '^name:' "$file"; then
            echo "FAIL $skill_name: missing 'name' field"
            errors=$((errors + 1))
        fi
        if ! grep -q '^description:' "$file"; then
            echo "FAIL $skill_name: missing 'description' field"
            errors=$((errors + 1))
        fi
    done
    if [ "$errors" -eq 0 ]; then
        echo "All skills valid."
    else
        echo ""
        echo "$errors error(s) found."
        exit 1
    fi

set dotenv-load := false

goose_dir := env("HOME") / ".config/goose/skills"
cursor_dir := env("HOME") / ".cursor/skills"
claude_dir := env("HOME") / ".claude/skills"
amp_dir := env("HOME") / ".config/amp/skills"
skills_src := justfile_directory() / "skills"

default:
    @just --list

# Deploy all skills to Goose, Cursor, Claude Code, and Amp via symlinks
deploy:
    #!/usr/bin/env bash
    set -euo pipefail
    src="{{skills_src}}"
    targets=(
        "{{goose_dir}}"
        "{{cursor_dir}}"
        "{{claude_dir}}"
        "{{amp_dir}}"
    )
    labels=("Goose" "Cursor" "Claude" "Amp")

    for dir in "${targets[@]}"; do
        mkdir -p "$dir"
    done

    for skill_dir in "$src"/*/; do
        skill_name=$(basename "$skill_dir")
        if [ ! -f "$skill_dir/SKILL.md" ]; then
            echo "SKIP $skill_name (no SKILL.md)"
            continue
        fi

        for dir in "${targets[@]}"; do
            rm -rf "$dir/$skill_name"
            ln -sf "$skill_dir" "$dir/$skill_name"
        done

        echo "  OK $skill_name"
    done
    echo ""
    echo "Deployed to:"
    for i in "${!targets[@]}"; do
        echo "  ${labels[$i]}  → ${targets[$i]}"
    done

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

# Pull latest from git and redeploy all skills
sync:
    #!/usr/bin/env bash
    set -euo pipefail
    cd "{{justfile_directory()}}"
    echo "Pulling latest changes..."
    git pull --rebase --quiet origin "$(git rev-parse --abbrev-ref HEAD)" 2>&1
    echo "Redeploying skills..."
    just deploy

# Install a daily launchd job (macOS) to sync skills from git
install-sync:
    #!/usr/bin/env bash
    set -euo pipefail
    plist_name="com.skills.sync"
    plist_path="$HOME/Library/LaunchAgents/${plist_name}.plist"
    repo_dir="{{justfile_directory()}}"
    just_bin="$(which just)"
    log_dir="$HOME/.local/log"

    mkdir -p "$HOME/Library/LaunchAgents" "$log_dir"

    cat > "$plist_path" <<PLIST
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
      "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
      <key>Label</key>
      <string>${plist_name}</string>
      <key>ProgramArguments</key>
      <array>
        <string>${just_bin}</string>
        <string>sync</string>
      </array>
      <key>WorkingDirectory</key>
      <string>${repo_dir}</string>
      <key>StartCalendarInterval</key>
      <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
      </dict>
      <key>StandardOutPath</key>
      <string>${log_dir}/skills-sync.log</string>
      <key>StandardErrorPath</key>
      <string>${log_dir}/skills-sync.log</string>
      <key>EnvironmentVariables</key>
      <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>${HOME}</string>
      </dict>
    </dict>
    </plist>
    PLIST

    # unload first if already loaded, then load
    launchctl bootout "gui/$(id -u)/${plist_name}" 2>/dev/null || true
    launchctl bootstrap "gui/$(id -u)" "$plist_path"

    echo "Installed daily sync (9:00 AM):"
    echo "  Plist  → $plist_path"
    echo "  Log    → $log_dir/skills-sync.log"
    echo ""
    echo "To run immediately:  just sync"
    echo "To uninstall:        just uninstall-sync"

# Remove the daily sync launchd job
uninstall-sync:
    #!/usr/bin/env bash
    set -euo pipefail
    plist_name="com.skills.sync"
    plist_path="$HOME/Library/LaunchAgents/${plist_name}.plist"

    launchctl bootout "gui/$(id -u)/${plist_name}" 2>/dev/null || true
    rm -f "$plist_path"
    echo "Removed daily sync job."

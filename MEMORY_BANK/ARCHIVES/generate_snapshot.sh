#!/usr/bin/env bash
# ============================================================
# ORACLE SYSTEM SNAPSHOT GENERATOR
# Preserves intellectual record before filesystem cleanup
# Usage: bash generate_snapshot.sh 2>/dev/null | tee SYSTEM_SNAPSHOT_20260217.md
# ============================================================
HOME_DIR="/home/nachochi"
SNAP_DATE=$(date '+%Y-%m-%d %H:%M:%S')

EXCLUDE_DIRS=( "anaconda" "miniconda" ".cargo" "node_modules" "/opt/" ".local/share/zinit" ".local/share/Steam" ".bash_it" ".bash-syntax" "snapd" )

should_skip() {
  local path="$1"
  for ex in "${EXCLUDE_DIRS[@]}"; do
    [[ "$path" == *"$ex"* ]] && return 0
  done
  return 1
}

echo "# 🧠 NACHOCHI SYSTEM SNAPSHOT — PRE-CLEANUP"
echo "**Generated:** $SNAP_DATE"
echo ""
echo "> This document preserves the complete intellectual record of the system"
echo "> before disk cleanup. No source code, git history, or documentation is deleted."
echo "> Only compiled artifacts (target/), broken downloads (.part), and caches are removed."
echo ""

# ============================================================
echo "---"
echo "## 💾 DISK STATE AT SNAPSHOT TIME"
echo '```'
df -h / | head -2
echo '```'
echo ""
echo "**Top space consumers:**"
echo '```'
du -sh $HOME_DIR/* 2>/dev/null | sort -rh | head -25
echo '```'
echo ""

# ============================================================
echo "---"
echo "## 🗂️ PROJECT DIRECTORY TREE (depth 4, no system dirs)"
echo '```'
find $HOME_DIR -maxdepth 4 \
  -not -path "*/.git/*" \
  -not -path "*/target/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/node_modules/*" \
  -not -path "*/anaconda*" \
  -not -path "*/miniconda*" \
  -not -path "*/.cargo*" \
  -not -path "*/.local/share/zinit*" \
  -not -path "*/.local/share/Steam*" \
  -not -path "*/.bash*" \
  -not -path "*/venv/*" \
  -not -path "*/env/lib/*" \
  -not -path "*/.zinit*" \
  -not -path "*/snapd*" \
  2>/dev/null | sort | sed "s|$HOME_DIR/||" | grep -v "^\." | head -600
echo '```'
echo ""

# ============================================================
echo "---"
echo "## 🦀 RUST PROJECTS — Target Dirs Being Freed"
echo ""
echo "| Project | Path | Target Size | Binaries |"
echo "|---|---|---|---|"
find $HOME_DIR -name "Cargo.toml" \
  -not -path "*/target/*" \
  -not -path "*/.cargo/*" \
  -not -path "*/anaconda*" \
  -not -path "*/miniconda*" \
  -not -path "*/node_modules/*" \
  2>/dev/null | while read cargo; do
  proj_dir=$(dirname "$cargo")
  proj_name=$(basename "$proj_dir")
  if [ -d "$proj_dir/target" ]; then
    tsize=$(du -sh "$proj_dir/target" 2>/dev/null | cut -f1)
    bins=$(find "$proj_dir/target/debug" "$proj_dir/target/release" -maxdepth 1 -type f -executable 2>/dev/null | xargs -I{} basename {} | tr '\n' ', ' | sed 's/,$//')
    [ -z "$bins" ] && bins="(no top-level bins)"
    echo "| \`$proj_name\` | \`${proj_dir#$HOME_DIR/}\` | **$tsize** | $bins |"
  fi
done
echo ""

# ============================================================
echo "---"
echo "## 📦 RUST PROJECT DETAILS (Cargo.toml + git log)"
echo ""
find $HOME_DIR -name "Cargo.toml" \
  -not -path "*/target/*" \
  -not -path "*/.cargo/*" \
  -not -path "*/anaconda*" \
  -not -path "*/miniconda*" \
  -not -path "*/node_modules/*" \
  2>/dev/null | sort | while read cargo; do
  proj_dir=$(dirname "$cargo")
  # Only include workspace roots or projects with a target dir
  if [ -d "$proj_dir/target" ] || grep -q '^\[workspace\]' "$cargo" 2>/dev/null; then
    proj_name=$(basename "$proj_dir")
    echo "### 🦀 \`$proj_name\`"
    echo "**Full path:** \`$proj_dir\`"
    
    # Size breakdown
    if [ -d "$proj_dir/target" ]; then
      echo "**Target size (freed):** $(du -sh "$proj_dir/target" 2>/dev/null | cut -f1)"
    fi
    
    # Git log
    if git -C "$proj_dir" rev-parse --git-dir > /dev/null 2>&1; then
      echo "**Git log (last 15):**"
      echo '```'
      git -C "$proj_dir" log --oneline -15 2>/dev/null
      echo '```'
      echo "**Remote:** $(git -C "$proj_dir" remote get-url origin 2>/dev/null || echo 'local only')"
    fi
    
    # Cargo.toml
    echo "**Cargo.toml:**"
    echo '```toml'
    cat "$cargo" 2>/dev/null
    echo '```'
    
    # README
    if [ -f "$proj_dir/README.md" ]; then
      echo "**README (first 50 lines):**"
      echo '```markdown'
      head -50 "$proj_dir/README.md"
      echo '```'
    fi
    echo ""
  fi
done

# ============================================================
echo "---"
echo "## 🐍 PYTHON VIRTUAL ENVIRONMENTS (documented before potential cleanup)"
echo ""
echo "| Name | Parent Project | Size | Python Version |"
echo "|---|---|---|---|"
find $HOME_DIR -name "pyvenv.cfg" \
  -not -path "*/anaconda*" \
  -not -path "*/miniconda*" \
  2>/dev/null | while read venv_cfg; do
  venv_dir=$(dirname "$venv_cfg")
  venv_name=$(basename "$venv_dir")
  parent=$(basename "$(dirname "$venv_dir")")
  vsize=$(du -sh "$venv_dir" 2>/dev/null | cut -f1)
  py_ver=$(grep "^version" "$venv_cfg" 2>/dev/null | cut -d= -f2 | tr -d ' ')
  echo "| \`$venv_name\` | \`$parent\` | $vsize | Python $py_ver |"
done
echo ""

# ============================================================
echo "---"
echo "## 🗄️ ALL GIT REPOSITORIES (project-level)"
echo ""
find $HOME_DIR -name ".git" -type d \
  -not -path "*/anaconda*" \
  -not -path "*/miniconda*" \
  -not -path "*/.cargo*" \
  -not -path "*/.local/share/zinit*" \
  -not -path "*/.local/share/Steam*" \
  -not -path "*/snapd*" \
  2>/dev/null | sort | while read gitdir; do
  repo_dir=$(dirname "$gitdir")
  should_skip "$repo_dir" && continue
  repo_name=$(basename "$repo_dir")
  echo "### 📦 \`$repo_name\`"
  echo "**Path:** \`${repo_dir#$HOME_DIR/}\`"
  remote=$(git -C "$repo_dir" remote get-url origin 2>/dev/null)
  [ -n "$remote" ] && echo "**Remote:** $remote"
  echo "**Last 10 commits:**"
  echo '```'
  git -C "$repo_dir" log --oneline -10 2>/dev/null || echo "(no commits)"
  echo '```'
  echo ""
done

# ============================================================
echo "---"
echo "## 📁 DOWNLOADS FOLDER — Complete Manifest"
echo '```'
ls -lah $HOME_DIR/Downloads/ 2>/dev/null
echo '```'
echo ""
echo "**Files to be cleaned (broken/obsolete):**"
echo "- \`@GBA - EverDrive GBA 2022-08-08.qe9r-DyL.zip.part\` — 7.4G broken partial download"
echo "- \`IyDEUvlU.html.part\` — 0 bytes broken download"
echo "- \`waveterm-linux-x64-0.9.3.pkg.tar.zst\` — 109M old version (replaced)"
echo "- \`Notion Setup 4.15.3.exe\` — 84M Windows installer (irrelevant on Linux)"
echo "- \`droidkit-en-setup.exe\` — 21M Windows installer (irrelevant on Linux)"
echo ""

# ============================================================
echo "---"
echo "## 📚 KEY README FILES"
echo ""
# Only top-level project READMEs (not deeply nested)
find $HOME_DIR -maxdepth 3 -name "README.md" \
  -not -path "*/target/*" \
  -not -path "*/.git/*" \
  -not -path "*/anaconda*" \
  -not -path "*/miniconda*" \
  -not -path "*/node_modules/*" \
  -not -path "*/.local*" \
  -not -path "*/.cargo*" \
  2>/dev/null | sort | while read readme; do
  echo "### 📄 \`${readme#$HOME_DIR/}\`"
  echo '```markdown'
  head -40 "$readme" 2>/dev/null
  echo '```'
  echo ""
done

# ============================================================
echo "---"
echo "## 🔧 JUJUTSU (JJ) REPOS"
echo ""
find $HOME_DIR -name ".jj" -type d \
  -not -path "*/anaconda*" \
  2>/dev/null | while read jjdir; do
  repo_dir=$(dirname "$jjdir")
  echo "### \`$(basename $repo_dir)\` at \`${repo_dir#$HOME_DIR/}\`"
  echo '```'
  jj -R "$repo_dir" log --no-graph -n 10 2>/dev/null || echo "(jj not available)"
  echo '```'
  echo ""
done

# ============================================================
echo "---"
echo "## ✅ SNAPSHOT COMPLETE"
echo ""
echo "**Safe to delete after this snapshot:**"
echo "| Item | Size | Reason |"
echo "|---|---|---|"
echo "| All Rust \`target/\` dirs | ~16G | Compiled artifacts — rebuild with \`cargo build\` |"
echo "| \`Downloads/@GBA*.part\` | 7.4G | Broken partial download |"
echo "| \`Downloads/waveterm*.zst\` | 109M | Old version already superseded |"
echo "| \`Downloads/*.exe\` | ~105M | Windows installers, irrelevant on Linux |"
echo ""
echo "**To rebuild any Rust project:** \`cd <path> && cargo build --release\`"
echo "**To rebuild any Python venv:** \`python -m venv venv && pip install -r requirements.txt\`"
echo "**To re-download Cursor latest:** \`curl -L https://downloader.cursor.sh/linux/appImage/x64 -o cursor-latest.AppImage\`"

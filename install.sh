#!/usr/bin/env bash
# Friends & Family agent starter — install.sh
#
# Overlays this starter onto ~/.pi/agent/ and installs the shared skills into
# ~/.agents/skills/. Safe: backs up any existing ~/.pi/agent first. Needs no
# git — it works from an unzipped folder.
#
# Usage:  ./install.sh

set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="${HOME}/.pi/agent"
SHARED_SKILLS="${HOME}/.agents/skills"
HERMES_DIR="${HOME}/.hermes"
BACKUP_DIR="${HOME}/.pi/agent.bak.$(date +%Y%m%d-%H%M%S)"

# ── Pre-flight checks ──────────────────────────────────────────────────────
echo "Checking prerequisites (warnings only — install will still proceed):"
for tool in git node npm herdr hermes; do
  if command -v "$tool" >/dev/null 2>&1; then
    printf '  %-8s %s\n' "$tool" "ok"
  else
    printf '  %-8s %s\n' "$tool" "MISSING (install it — see GETTING-STARTED.md)"
  fi
done
if [[ -z "${OPENROUTER_API_KEY:-}" ]]; then
  echo "  note: OPENROUTER_API_KEY is not set in this shell — set it before launching the agent"
fi

# ── Back up + create the target ────────────────────────────────────────────
if [[ -d "$TARGET_DIR" ]]; then
  echo "Backing up existing ~/.pi/agent -> $BACKUP_DIR"
  cp -r "$TARGET_DIR" "$BACKUP_DIR"
else
  echo "Creating fresh ~/.pi/agent ..."
  mkdir -p "$TARGET_DIR"
fi

# ── Overlay the portable core ─────────────────────────────────────────────
echo "Overlaying starter onto ~/.pi/agent ..."
rsync -a \
  --exclude='/.git' \
  --exclude='/README.md' \
  --exclude='/GETTING-STARTED.md' \
  --exclude='/install.sh' \
  --exclude='/docs' \
  --exclude='/herdr' \
  --exclude='/skills' \
  --exclude='/TODO.md' \
  "$REPO_DIR/" "$TARGET_DIR/"

# ── Skills -> the shared Agent Skills directory ───────────────────────────
if [[ -d "$REPO_DIR/skills" ]]; then
  mkdir -p "$SHARED_SKILLS"
  rsync -a "$REPO_DIR/skills/" "$SHARED_SKILLS/"
  echo "Skills installed to $SHARED_SKILLS"
fi

# ── Wire Hermes to read the shared skills dir (idempotent) ────────────────
if command -v hermes >/dev/null 2>&1 || [[ -d "$HERMES_DIR" ]]; then
  mkdir -p "$HERMES_DIR"
  python3 - "$HERMES_DIR/config.yaml" "${SHARED_SKILLS/#$HOME/~}" <<'PY'
import os, pathlib, sys
try:
    import yaml
except ImportError:
    print("  PyYAML unavailable — cannot repair ~/.hermes/config.yaml (install python-yaml)"); sys.exit(0)
cfg_path = pathlib.Path(sys.argv[1]); shared_raw = sys.argv[2]
shared = os.path.expanduser(shared_raw).rstrip("/")
existed = cfg_path.exists()
data = {}
if existed:
    try: data = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        print(f"  ~/.hermes/config.yaml is not valid YAML ({exc}) — leaving untouched"); sys.exit(0)
if not isinstance(data, dict):
    print("  ~/.hermes/config.yaml top level is not a mapping — leaving untouched"); sys.exit(0)
skills = data.get("skills") if isinstance(data.get("skills"), dict) else {}
def norm(e): return os.path.expanduser(str(e)).rstrip("/")
dirs = skills.get("external_dirs")
if isinstance(dirs, str): dirs = [dirs]
if not isinstance(dirs, list): dirs = []
changed = False
if shared not in [norm(d) for d in dirs]:
    dirs.append(shared_raw); changed = True
if skills.get("external_dirs") != dirs:
    skills["external_dirs"] = dirs; changed = True
if norm(skills.get("create_dir", "")) != shared:
    skills["create_dir"] = shared_raw; changed = True
if changed:
    data["skills"] = skills
    cfg_path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
    if not existed: os.chmod(cfg_path, 0o600)
    print(f"  Hermes skills wired -> {shared}")
else:
    print(f"  Hermes skills already wired -> {shared}")
PY
else
  echo "Hermes not detected — skipping ~/.hermes/config.yaml wiring."
fi

# ── Seed a starter TODO only if the user has none ─────────────────────────
if [[ -f "$REPO_DIR/TODO.md" && ! -f "${HOME}/TODO.md" ]]; then
  cp "$REPO_DIR/TODO.md" "${HOME}/TODO.md"
  echo "Seeded ${HOME}/TODO.md from the starter checklist."
fi

echo ""
echo "Done."
echo "  Backup: $BACKUP_DIR"
echo "  Target: $TARGET_DIR"
echo ""
echo "Next:"
echo "  1. Set OPENROUTER_API_KEY (see GETTING-STARTED.md)."
echo "  2. Install herdr's Hermes integration:  herdr integration install hermes"
echo "  3. Apply the single-tab layout (optional):  python3 herdr/apply.py --apply"
echo "  4. Restart any running agent sessions to pick up the new files."

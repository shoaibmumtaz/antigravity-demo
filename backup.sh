#!/usr/bin/env bash
# Local-only backup: commits the project, tags it, and writes restorable copies
# to _Backups. Nothing here pushes to a remote.
#
#   ./backup.sh "what changed"   save a backup
#   ./backup.sh list             show saved backups
set -euo pipefail

cd "$(dirname "$0")"
BACKUPS="${BACKUPS:-_Backups}"

if [ "${1:-}" = "list" ]; then
  git tag -l 'backup-*' --sort=-creatordate --format='%(refname:short)  %(contents:subject)'
  exit 0
fi

msg="${1:?Usage: ./backup.sh \"what changed\"  |  ./backup.sh list}"

git add -A
if ! git diff --cached --quiet; then
  git commit -q -m "$msg"
fi

if [ -n "$(git tag -l 'backup-*' --points-at HEAD)" ]; then
  echo "No changes since the last backup."
  exit 0
fi

tag="backup-$(date +%Y-%m-%d_%H%M%S)"
git tag -a "$tag" -m "$msg"

mkdir -p "$BACKUPS"
git archive --format=zip --prefix="$tag/" -o "$BACKUPS/$tag.zip" "$tag"
git bundle create -q "$BACKUPS/history.bundle" --all

echo "Saved $tag"
echo "  $BACKUPS/$tag.zip"
echo "  $BACKUPS/history.bundle"

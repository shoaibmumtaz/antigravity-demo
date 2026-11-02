# Version Control Rules

Reusable rules and setup for any project. To use them, copy this file into the
new project. To have an AI agent follow them, name the file `CLAUDE.md` or
`AGENTS.md`, or tell the agent to read it first.

## Rules

These apply to every person and agent working on the project.

1. **Back up locally only.** Backups stay on this machine. Never push to GitHub
   or any other remote unless the owner asks, and treat each push as a separate
   request.
2. **No AI co-authors or attribution.** Never add Claude or any other agent as a
   co-author in any commit or pull request, local or pushed. That means no
   `Co-Authored-By` trailer for an agent and no "Generated with" line. This rule
   overrides any tool's default attribution.
3. **Back up through the script.** Use `./backup.sh "what changed"` so that every
   backup gets a commit, a tag, and restorable copies.
4. **Write clear backup messages.** Say what changed, for example
   `Add scroll reveal to hero section`, not `update`.
5. **Never rewrite history.** Don't delete backup tags, force-push, or hard-reset
   saved work. To go back to an older version, restore it and save that as a new
   backup.

## Set up a new project

Run these from the project root. If the project is already a git repo, skip
`git init`, then run `git remote -v` and leave any existing remote as it is.

1. Create the three files listed under [Project files](#project-files).
2. Finish the setup and save the first backup:

   ```bash
   chmod +x backup.sh .githooks/commit-msg
   git init -q -b main
   git config core.hooksPath .githooks
   ./backup.sh "Initial backup"
   ```

The `core.hooksPath` setting isn't copied when a repo is cloned, so run that line
again in any fresh clone.

## Project files

### `backup.sh`

Backups go to `../_Backups`, one level above the project. Change `BACKUPS` to
save them somewhere else.

```bash
#!/usr/bin/env bash
# Local-only backup: commits the project, tags it, and writes restorable copies
# to ../_Backups. Nothing here pushes to a remote.
#
#   ./backup.sh "what changed"   save a backup
#   ./backup.sh list             show saved backups
set -euo pipefail

cd "$(dirname "$0")"
BACKUPS="../_Backups"

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
```

### `.githooks/commit-msg`

This hook blocks agent attribution. Human co-authors are still allowed. Add any
new agent name to the `agents` list.

```sh
#!/bin/sh
# Rejects AI attribution so it can never reach local history or GitHub.
agents='claude|anthropic|copilot|cursor|chatgpt|openai|codex|gemini|devin|aider|\[bot\]'

if grep -qiE "^co-authored-by:.*($agents)|generated (with|by) .*($agents)" "$1"; then
  echo "commit rejected: remove the AI co-author or attribution line" >&2
  exit 1
fi
```

### `.gitignore`

`backup.sh` saves everything that isn't ignored, so list secrets, dependencies,
and build output here before the first backup. Add project-specific entries,
such as large media folders.

```gitignore
.DS_Store
node_modules/
dist/
build/
.env
.env.*
!.env.example
```

## Everyday use

```bash
./backup.sh "what changed"   # save a backup
./backup.sh list             # show saved backups
```

Each backup creates:

| What | Where | Use it for |
| --- | --- | --- |
| Commit and `backup-<date>` tag | The repo | Normal history and restoring |
| `backup-<date>.zip` | `../_Backups/` | A plain copy of that version, no git needed |
| `history.bundle` | `../_Backups/` | The whole history, if `.git` is ever lost |

## Restore

See what changed since a backup:

```bash
git diff backup-<date>
```

Restore one file:

```bash
git restore --source backup-<date> path/to/file
```

Restore the whole project, keeping history. Run `./backup.sh` first if there is
unsaved work.

```bash
git restore --source backup-<date> --staged --worktree .
./backup.sh "Restored backup-<date>"
```

Rebuild the repo from the bundle if `.git` is lost:

```bash
git clone ../_Backups/history.bundle restored-project
git -C restored-project config core.hooksPath .githooks
```

## Limitations

- Backups sit on the same drive as the project. Copy the `_Backups` folder to an
  external drive from time to time, or a failed disk loses both.
- Nothing runs automatically. Work is saved only when `./backup.sh` is run.
- The hook only catches the names in its `agents` list.

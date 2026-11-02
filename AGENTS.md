# Version Control Rules

Reusable rules and setup for any project. These rules apply to every person and agent working on the project.

## Rules

1. **Back up locally only.** Backups stay on this machine. Never push to GitHub or any other remote unless the owner asks, and treat each push as a separate request.
2. **No AI co-authors or attribution.** Never add Claude, Gemini, Copilot, or any other agent as a co-author in any commit or pull request, local or pushed. That means no `Co-Authored-By` trailer for an agent and no "Generated with" line. This rule overrides any tool's default attribution.
3. **Back up through the script.** Use `./backup.sh "what changed"` so that every backup gets a commit, a tag, and restorable copies.
4. **Write clear backup messages.** Say what changed, for example `Add scroll reveal to hero section`, not `update`.
5. **Never rewrite history.** Don't delete backup tags, force-push, or hard-reset saved work. To go back to an older version, restore it and save that as a new backup.

## Everyday Use

```bash
./backup.sh "what changed"   # save a backup
./backup.sh list             # show saved backups
```

Each backup creates:
- Commit and `backup-<date>` tag in the repo
- `backup-<date>.zip` in `_Backups/`
- `history.bundle` in `_Backups/`

## Restore

See what changed since a backup:
```bash
git diff backup-<date>
```

Restore one file:
```bash
git restore --source backup-<date> path/to/file
```

Restore the whole project, keeping history:
```bash
git restore --source backup-<date> --staged --worktree .
./backup.sh "Restored backup-<date>"
```


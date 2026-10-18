@~/sopel/CLAUDE.md

# sopel-slap (fork)

The owner's fork of the upstream `sopel-irc/sopel-slap` plugin (entry point
`slap`). Work happens on the **`extend`** branch; `master` follows upstream.
Remotes: `origin` (the fork) and `upstream`. Bring upstream changes in by
merging `upstream/master` into `extend`.

## What the fork adds

- `.slap` / `.slaps` with phrases loaded from JSON files, including a
  channel-specific list, and `.poke` / `.pokes`.
- Phrase files are re-read automatically when they change (mtime check in
  `util.py`); `.reload-slaps` forces it.

## Files

- `sopel_slap/verbs/verbs.json`, `sopel_slap/verbs/example.json`,
  `sopel_slap/pokes/pokes.json`: the owner's phrase lists. Git-ignored; only
  the `.example` files are committed. sopel-ui's "Slaps & pokes" page edits
  them.
- `config.py`: the `[slap]` section (`verbs`, `reflexive`).
- `plugin.py` (commands), `util.py` (loading and choosing phrases).

Keep the upstream code style (it has its own lint setup in
`dev-requirements.txt` / `Makefile`), and keep fork changes small so merges
from upstream stay easy.

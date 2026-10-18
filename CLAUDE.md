@~/sopel/CLAUDE.md

# sopel-slap (fork)

The owner's fork of the upstream `sopel-irc/sopel-slap` plugin (entry point
`slap`). Work happens on the **`extend`** branch; `master` follows upstream.
Remotes: `origin` (the fork) and `upstream`. Bring upstream changes in by
merging `upstream/master` into `extend`.

## What the fork adds

- `.slap` / `.slaps` with phrases from the bot's database, plus extra
  phrases per channel, and `.poke` / `.pokes`.
- Changes made elsewhere are picked up on the next use; `.reload-slaps`
  forces a reload.

## Storage

Phrase lists are in the bot's database (defined in `util.py`): `slap_lists`
(`slaps`, `pokes`, or a channel like `#example`), `slap_phrases` (list,
position, phrase) and `slap_state` (a version every writer raises; the plugin
reloads when it changes, so sopel-ui's "Slaps & pokes" edits apply at once).
Old JSON files (`verbs/verbs.json`, `verbs/channels/*.json`,
`pokes/pokes.json`) are imported once into an empty database and moved to
`<homedir>/backups/sopel-slap/`; only `.example` files are committed.

- `config.py`: the `[slap]` section (`verbs`, `reflexive`).
- `plugin.py` (commands; reloads `util` on every plugin reload, so changes
  there need no restart), `util.py` (storage and choosing phrases).

Keep the upstream code style (it has its own lint setup in
`dev-requirements.txt` / `Makefile`), and keep fork changes small so merges
from upstream stay easy.

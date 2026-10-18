"""Slap utilities

Part of `sopel-slap`.

Copyright 2024, dgw, technobabbl.es

https://sopel.chat
"""

from __future__ import annotations
from collections import defaultdict

import random
from typing import TYPE_CHECKING

import json
import logging
import os
import shutil

from sopel import formatting, tools
from sqlalchemy import Column, Integer, MetaData, String, Table, Text, insert, select
from sqlalchemy.exc import SQLAlchemyError

import time

LOGGER = logging.getLogger("sopel.externals.slap")

# Holds shuffled verb lists for each channel
channel_verb_queues = defaultdict(list)

if TYPE_CHECKING:
    from sopel.bot import SopelWrapper
    from sopel.trigger import Trigger


# Phrase lists live in the bot's database:
#   slap_lists    one row per list: "slaps" (every channel), "pokes", or a
#                 channel name ("#example") for extra slaps used only there
#   slap_phrases  the phrases of each list, in order
#   slap_state    a version number raised by every writer (this plugin, Sopel
#                 UI), so edits made elsewhere are picked up on the next use
metadata = MetaData()
lists_table = Table(
    "slap_lists", metadata,
    Column("name", String(64), primary_key=True),
)
phrases_table = Table(
    "slap_phrases", metadata,
    Column("id", Integer, primary_key=True),
    Column("list", String(64), nullable=False, index=True),
    Column("position", Integer, nullable=False),
    Column("phrase", Text, nullable=False),
)
state_table = Table(
    "slap_state", metadata,
    Column("name", String(32), primary_key=True),
    Column("version", Integer, nullable=False, default=0),
)

VERBS = []  # slaps for every channel
CHANNEL_VERBS = {}  # "#channel" -> extra slaps used only there
POKES = []
_loaded_version = None


def _version(bot):
    with bot.db.engine.connect() as conn:
        return conn.execute(
            select(state_table.c.version).where(state_table.c.name == "phrases")
        ).scalar() or 0


def load_phrases(bot):
    """Read every list from the database."""
    global VERBS, CHANNEL_VERBS, POKES, _loaded_version
    version = _version(bot)
    lists = {}
    with bot.db.engine.connect() as conn:
        for (name,) in conn.execute(select(lists_table.c.name)):
            lists[name] = []
        rows = conn.execute(
            select(phrases_table.c.list, phrases_table.c.phrase)
            .order_by(phrases_table.c.list, phrases_table.c.position, phrases_table.c.id)
        )
        for name, phrase in rows:
            lists.setdefault(name, []).append(phrase)
    VERBS = lists.pop("slaps", [])
    POKES = lists.pop("pokes", [])
    random.shuffle(POKES)
    CHANNEL_VERBS = {name.lower(): phrases for name, phrases in lists.items()}
    _loaded_version = version
    # Start the per-channel queues afresh with the new lists.
    channel_verb_queues.clear()


def refresh_phrases(bot):
    """Reload the lists if they changed since they were loaded."""
    try:
        if _version(bot) != _loaded_version:
            load_phrases(bot)
    except SQLAlchemyError:
        LOGGER.exception("Could not read the slap phrases")


# Files older versions kept in the package folder; imported once into an
# empty database, then moved to <bot home>/backups/sopel-slap/.
PACKAGE_DIR = os.path.dirname(__file__)
LEGACY_FILES = [
    ("slaps", os.path.join(PACKAGE_DIR, "verbs", "verbs.json")),
    ("pokes", os.path.join(PACKAGE_DIR, "pokes", "pokes.json")),
]
LEGACY_CHANNEL_DIR = os.path.join(PACKAGE_DIR, "verbs", "channels")


def migrate_legacy_files(bot):
    files = list(LEGACY_FILES)
    if os.path.isdir(LEGACY_CHANNEL_DIR):
        for name in sorted(os.listdir(LEGACY_CHANNEL_DIR)):
            if name.endswith(".json"):
                files.append(("#" + name[:-len(".json")].lower(), os.path.join(LEGACY_CHANNEL_DIR, name)))
    files = [(name, path) for name, path in files if os.path.isfile(path) and not os.path.islink(path)]
    if not files:
        return
    backup_dir = os.path.join(bot.config.core.homedir, "backups", "sopel-slap")
    stamp = time.strftime("%Y%m%d-%H%M%S")
    try:
        with bot.db.engine.begin() as conn:
            if conn.execute(select(lists_table).limit(1)).first():
                LOGGER.warning("Old phrase files not imported: the database already has phrase lists")
            else:
                for name, path in files:
                    with open(path, encoding="utf-8") as f:
                        phrases = [str(p) for p in json.load(f)]
                    conn.execute(insert(lists_table).values(name=name))
                    if phrases:
                        conn.execute(insert(phrases_table), [
                            {"list": name, "position": n, "phrase": p} for n, p in enumerate(phrases)])
                conn.execute(insert(state_table).values(name="phrases", version=1))
                LOGGER.info("Imported %d phrase files into the database", len(files))
        os.makedirs(backup_dir, exist_ok=True)
        for name, path in files:
            label = "channels-" + name[1:] if name.startswith("#") else name
            shutil.move(path, os.path.join(backup_dir, f"{label}.json.{stamp}"))
        # links left at old paths now point nowhere
        verbs_dir = os.path.join(PACKAGE_DIR, "verbs")
        for name in os.listdir(verbs_dir):
            path = os.path.join(verbs_dir, name)
            if os.path.islink(path) and not os.path.exists(path):
                os.remove(path)
    except (OSError, ValueError, SQLAlchemyError):
        LOGGER.exception("Could not import the old phrase files")


def setup(bot):
    metadata.create_all(bot.db.engine)
    migrate_legacy_files(bot)
    load_phrases(bot)


# Kept for the .reload-slaps / .reload-pokes commands.
def load_slaps(bot):
    load_phrases(bot)


load_pokes = load_slaps


def slap(bot: SopelWrapper, trigger: Trigger, target: str):
    """Do the slapping."""
    # the target could contain formatting control codes, so strip those
    target = formatting.plain(target)

    # ensure target is an Identifier to increase reliability of "is nick" check
    if not isinstance(target, tools.Identifier):
        if hasattr(bot, "make_identifier"):
            target = bot.make_identifier(target)
        else:
            # TODO: remove once Sopel 7 support is dropped
            target = tools.Identifier(target)

    if not target.is_nick():
        bot.reply("You can't slap the whole channel!")
        return

    if target not in bot.channels[trigger.sender].users:
        if not trigger.ctcp:
            # only reply if a command was used; ignore CTCP ACTIONs
            # we don't want the bot to be annoying to people who do "/me slaps"
            # without realizing (or remembering) that the bot responds to it
            bot.reply("You can't slap someone who isn't here!")

        return

    if target == bot.nick:
        if not trigger.admin:
            target = trigger.nick
        else:
            target = bot.settings.slap.reflexive

    if not trigger.admin and (
        target == bot.config.core.owner or target in bot.config.core.admins
    ):
        target = trigger.nick

    channel = trigger.sender.lower()
    global_verbs = bot.settings.slap.verbs

    refresh_phrases(bot)

    # The general slaps, plus this channel's own ones if it has a list.
    verbs = VERBS + CHANNEL_VERBS.get(channel, [])

    # Use per-channel shuffled queue to reduce repetition
    queue = channel_verb_queues[channel]

    if not queue:
        if not verbs:
            bot.reply("No slap verbs yet. Add some in Sopel UI.")
            return
        queue.extend(verbs)
        random.shuffle(queue)

    if not queue:
        bot.reply("Slap queue is unexpectedly empty.")
        return

    verb = queue.pop()

    # verb = random.choice(bot.settings.slap.verbs)
    # verb = random.choice(verbs)

    bot.action(f"{verb} {target}")


def poke(bot: SopelWrapper, trigger: Trigger, target: str):
    global POKES
    target = formatting.plain(target)

    if not isinstance(target, tools.Identifier):
        target = tools.Identifier(target)

    if not target.is_nick():
        bot.reply("You can't poke the whole channel!")
        return

    if target not in bot.channels[trigger.sender].users:
        if not trigger.ctcp:
            bot.reply("You can't poke someone who isn't here!")
        return

    if target == bot.nick:
        if not trigger.admin:
            target = trigger.nick
        else:
            target = bot.settings.slap.reflexive

    if not trigger.admin and (
        target == bot.config.core.owner or target in bot.config.core.admins
    ):
        target = trigger.nick

    refresh_phrases(bot)

    if not POKES:
        bot.say("No poke actions yet. Add some in Sopel UI.")
        return

    # verb = random.choice(POKES)
    random.seed(time.time())  # ensure varied randomness per second
    verb = random.choice(POKES)
    bot.action(f"{verb} {target}")

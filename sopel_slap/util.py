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
import os

from sopel import formatting, tools

import time

# Holds shuffled verb lists for each channel
channel_verb_queues = defaultdict(list)

if TYPE_CHECKING:
    from sopel.bot import SopelWrapper
    from sopel.trigger import Trigger


VERBS_PATH = os.path.join(os.path.dirname(__file__), "verbs", "verbs.json")
# Extra slaps for one channel each: verbs/channels/<channel>.json, named after
# the channel without its "#" (e.g. example.json for #example).
CHANNEL_VERBS_DIR = os.path.join(os.path.dirname(__file__), "verbs", "channels")

VERBS = []
CHANNEL_VERBS = {}

POKES_PATH = os.path.join(os.path.dirname(__file__), "pokes", "pokes.json")
POKES = []

# Modification times of the JSON files as of the last load, so edits made
# outside the bot (by hand or from Sopel UI) are picked up automatically.
_slaps_mtime = None
_pokes_mtime = None


def _mtimes(*paths):
    result = []
    for path in paths:
        try:
            result.append(os.stat(path).st_mtime_ns)
        except OSError:
            result.append(None)
    return tuple(result)


def _channel_files():
    """The channel phrase files, as {channel name without "#": path}."""
    try:
        names = sorted(os.listdir(CHANNEL_VERBS_DIR))
    except OSError:
        return {}
    return {
        name[:-len(".json")].lower(): os.path.join(CHANNEL_VERBS_DIR, name)
        for name in names
        if name.endswith(".json")
    }


def _slaps_state():
    files = _channel_files()
    return (_mtimes(VERBS_PATH, *files.values()), tuple(files))


def refresh_slaps():
    """Reload the slap verbs if any of the JSON files changed since the last load."""
    if _slaps_state() != _slaps_mtime:
        load_slaps()


def refresh_pokes():
    """Reload the poke verbs if the JSON file changed since the last load."""
    if _mtimes(POKES_PATH) != _pokes_mtime:
        load_pokes()


def load_slaps():
    global VERBS, CHANNEL_VERBS, _slaps_mtime
    _slaps_mtime = _slaps_state()
    try:
        with open(VERBS_PATH, "r", encoding="utf-8") as f:
            VERBS = json.load(f)
    except Exception as e:
        print(f"[sopel-slap] Failed to load verbs.json: {e}")
        VERBS = []

    CHANNEL_VERBS = {}
    for channel, path in _channel_files().items():
        try:
            with open(path, "r", encoding="utf-8") as f:
                CHANNEL_VERBS[channel] = [str(verb) for verb in json.load(f)]
        except Exception as e:
            print(f"[sopel-slap] Failed to load channels/{os.path.basename(path)}: {e}")

    # Clear cached queues so we use updated lists
    channel_verb_queues.clear()
    print("[sopel-slap] Slap verbs reloaded.")


load_slaps()


def load_pokes():
    global POKES, _pokes_mtime
    _pokes_mtime = _mtimes(POKES_PATH)
    try:
        with open(POKES_PATH, "r", encoding="utf-8") as f:
            POKES = json.load(f)
        random.shuffle(POKES)
    except Exception as e:
        print(f"[sopel-slap] Failed to load pokes.json: {e}")
        POKES = []

    print("[sopel-slap] Poke verbs reloaded.")


load_pokes()


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

    refresh_slaps()

    # The general slaps, plus this channel's own ones if it has a file.
    verbs = VERBS + CHANNEL_VERBS.get(channel.lstrip("#&"), [])

    # Use per-channel shuffled queue to reduce repetition
    queue = channel_verb_queues[channel]

    if not queue:
        if not verbs:
            bot.reply("No slap verbs are loaded. Please reload or check JSON files.")
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

    refresh_pokes()

    if not POKES:
        bot.say("No poke actions loaded. Please reload or check pokes.json.")
        return

    # verb = random.choice(POKES)
    random.seed(time.time())  # ensure varied randomness per second
    verb = random.choice(POKES)
    bot.action(f"{verb} {target}")

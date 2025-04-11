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

# Holds shuffled verb lists for each channel
channel_verb_queues = defaultdict(list)

if TYPE_CHECKING:
    from sopel.bot import SopelWrapper
    from sopel.trigger import Trigger


VERBS_PATH = os.path.join(os.path.dirname(__file__), "verbs", "verbs.json")
PAKISTAN_VERBS_PATH = os.path.join(os.path.dirname(__file__), "verbs", "pakistan.json")

VERBS = []
PAKISTAN_VERBS = []

POKES_PATH = os.path.join(os.path.dirname(__file__), "pokes", "pokes.json")
POKES = []


def load_slaps():
    global VERBS, PAKISTAN_VERBS
    try:
        with open(VERBS_PATH, "r", encoding="utf-8") as f:
            VERBS = json.load(f)
    except Exception as e:
        print(f"[sopel-slap] Failed to load verbs.json: {e}")
        VERBS = []

    try:
        with open(PAKISTAN_VERBS_PATH, "r", encoding="utf-8") as f:
            PAKISTAN_VERBS = json.load(f)
    except Exception as e:
        print(f"[sopel-slap] Failed to load pakistan.json: {e}")
        PAKISTAN_VERBS = []

    # Clear cached queues so we use updated lists
    channel_verb_queues.clear()
    print("[sopel-slap] Slap verbs reloaded.")


load_slaps()


def load_pokes():
    global POKES
    try:
        with open(POKES_PATH, "r", encoding="utf-8") as f:
            POKES = json.load(f)
    except Exception as e:
        print(f"[sopel-slap] Failed to load pokes.json: {e}")
        POKES = []

    print("[sopel-slap] Poke verbs reloaded.")


load_pokes()


def slap(bot: SopelWrapper, trigger: Trigger, target: str):
    global VERBS, PAKISTAN_VERBS
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

    if channel == "#pakistan":
        # extra = bot.settings.slap.pakistan_verbs
        # verbs = global_verbs + extra
        verbs = VERBS + PAKISTAN_VERBS
    else:
        # verbs = global_verbs
        verbs = VERBS

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

    if not POKES:
        bot.say("No poke actions loaded. Please reload or check pokes.json.")
        return

    verb = random.choice(POKES)
    bot.action(f"{verb} {target}")

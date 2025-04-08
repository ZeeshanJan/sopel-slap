"""Slap utilities

Part of `sopel-slap`.

Copyright 2024, dgw, technobabbl.es

https://sopel.chat
"""

from __future__ import annotations
from collections import defaultdict

import random
from typing import TYPE_CHECKING

from sopel import formatting, tools

# Holds shuffled verb lists for each channel
channel_verb_queues = defaultdict(list)

if TYPE_CHECKING:
    from sopel.bot import SopelWrapper
    from sopel.trigger import Trigger


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

    if channel == "#pakistan":
        extra = bot.settings.slap.pakistan_verbs
        verbs = global_verbs + extra
    else:
        verbs = global_verbs

    # Use per-channel shuffled queue to reduce repetition
    queue = channel_verb_queues[channel]

    if not queue:
        queue.extend(verbs)
        random.shuffle(queue)

    verb = queue.pop()

    # verb = random.choice(bot.settings.slap.verbs)
    verb = random.choice(verbs)

    bot.action(f"{verb} {target}")

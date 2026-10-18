"""Sopel Slap plugin

Plugin for Sopel that lets users slap each other in fun ways.

Original slap.py copyright 2009, Michael Yanovich, yanovich.net.

This reworked version for Sopel 7.1+ copyright 2024, dgw, technobabbl.es

https://sopel.chat
"""

from __future__ import annotations

import importlib

from sopel import plugin

from . import util

# A plugin reload re-imports only this module; reload util too, so changes to
# it apply without restarting the bot.
importlib.reload(util)

# from .config import SlapSection, do_configure
from .util import slap, load_slaps, poke, load_pokes  # noqa: E402


def setup(bot):
    util.setup(bot)


"""
def setup(bot):
    bot.settings.define_section("slap", SlapSection)


def configure(settings):
    settings.define_section("slap", SlapSection)
    do_configure(settings.slap)
"""


@plugin.commands("slap", "slaps")
# @plugin.action_command('slaps')
@plugin.example(".slap Tr0ll_Extr4ordinair3")
def slap_command(bot, trigger):
    """Slap someone else in the channel."""
    target = trigger.group(3)

    if target is None:
        # `.slap` is a shortcut for slapping oneself, but not in CTCP ACTIONs
        if trigger.ctcp:
            return plugin.NOLIMIT

        target = trigger.nick
    else:
        target = target.strip()

    return slap(bot, trigger, target)


@plugin.command("reload-slaps")
@plugin.require_admin("Only admins can reload slap verbs.")
def reload_slaps_command(bot, trigger):
    load_slaps(bot)
    bot.say("Slap verbs reloaded.", trigger.sender)


@plugin.commands("poke", "pokes")
def poke_command(bot, trigger):
    target = trigger.group(3)
    if target is None:
        if trigger.ctcp:
            return plugin.NOLIMIT
        target = trigger.nick
    else:
        target = target.strip()

    return poke(bot, trigger, target)


@plugin.command("reload-pokes")
@plugin.require_admin("Only admins can reload poke verbs.")
def reload_pokes_command(bot, trigger):
    load_pokes(bot)
    bot.say("Poke verbs reloaded.", trigger.sender)

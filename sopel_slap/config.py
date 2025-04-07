"""Configuration definitions

Part of `sopel-slap`.

Copyright 2024, dgw, technobabbl.es

https://sopel.chat
"""

from __future__ import annotations

from sopel.config import types

VERBS = (
    "throws a naan at",
    "slaps with a soggy naan from last night's dawat",
    "pelts with expired Pakola bottles",
    "hurls a slipper like a desi ammi at",
    "summons aunties to gossip about",
    "spills hot chai on",
    "curses with buffering PTCL at",
    "sends rishtay aunties toward",
    "drops a 3-day-old biryani bucket on",
    "slaps with a hot roti",
    "pelts with stale samosas",
    "drops a tandoor on",
    "launches pakoras toward",
    "spills karak chai on",
    "splatters chutney on",
    "bonks with a madrasa register",
    "wraps in wedding tent cloth and throws at",
    "cracks a papad on",
    "flings jalebi at",
    "boils in nihari and pours on",
    "blames electricity theft on",
    "shouts “Oye!” and charges at",
    "sends a rishta proposal to",
    "throws a mango crate at",
    "yeets with food leftovers",
    "calls their dad to complain about",
    "throws biryani without aloo at",
    "blasts wedding dhol near",
    "whispers “no Qurbani meat for you” to",
    "makes late-night prank calls to",
    "pours leftover lassi on",
    "assigns channa delivery duty to",
    "pats lovingly and then slaps",
    "bonks with a stack of utility bills",
    "shouts “o chall !” while slapping",
    "throws a slow internet router at",
    "unleashes angry aunties at",
    "throws a bag of soggy fries at",
    "gives lecture about “hamare zamane mein” to",
    "hugs with malai boti hands and slaps",
    "calls their crush to tell secrets about",
    "disconnects their WiFi and stares",
    "throws dad’s old Nokia at",
    "throws leftover daal on",
    "pelts a mango at",
    "hurls a slipper at",
    "flings biryani at",
    "splatters chutney on",
    "smears haldi on",
    "smears leftover qorma on",
    "throws a daig of emotional damage at",
    "splashes Rooh Afza on",
    "slams into",
    "hurls a broken PIA tray table at",
    "smears melted kulfi all over",
    "pelts unpaid bijli bills at",
    "flings a chai-dipped biscuit at",
)


class SlapSection(types.StaticSection):
    verbs = types.ListAttribute("verbs", default=VERBS)
    """Verbs to choose from when slapping someone."""

    reflexive = types.ValidatedAttribute("reflexive", default="itself")
    """The reflexive pronoun the bot uses when someone slaps it."""


def do_configure(section: types.StaticSection):
    section.configure_setting(
        "verbs",
        "\nEnter verbs to choose from when slapping someone, one per line.\n\n"
        "Alternatively, press Enter twice without typing anything to write\n"
        "the current list (shown below) to your bot's .cfg file, where it\n"
        "can be edited using your favorite text editor.\n\n"
        "Current verb list:",
    )
    section.configure_setting(
        "reflexive",
        "What pronoun should the bot use for itself when someone slaps it?",
    )

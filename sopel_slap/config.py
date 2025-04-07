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

PAKISTAN_VERBS = (
    "wraps in chillmill` s smelly socks and hurls at",
    "stuffed RudeDude's ego into a cannon and fired at",
    "loads Mr_PresidenT's broken promises into a cannon and fired at",
    "baked Rapt's failed CSS attempts into a lasagna of regret and served to",
    "compressed Rapt's emotional damage logs into a floppy disk and frisbee'd at",
    "burned Stalker's playlist of heartbreak songs onto a CD and hurled at",
    "archived neeni's unpaid therapy bills into a USB and yeeted at",
    "stuffed Khurram's rejected rishta proposals into a tote bag and tossed at",
    "wrapped BK-'s paratha in tissue and frisbee'd it toward",
    "microwaved neeni's opinions and served them boiling to",
    "compressed TiN`TiN's corrupted Excel sheets into a floppy and missile-launched at",
    "rolled up midhat's 7 semesters of anatomy notes and smacked them across",
    "adjusted anetta^'s stethoscope like a crown and nodded disapprovingly at",
    "compared anetta^'s patience to the emotional chaos of",
    "asked anetta^ to diagnose the attention-seeking tendencies of",
    "watched Mr_PresidenT melt hearts with charm and then turned to cringe at",
    "took flirting lessons from Mr_PresidenT and immediately expelled",
    "saw Mr_PresidenT charm an entire channel and muted",
    "offered roses with Mr_PresidenT and handed expired ketchup to",
    "asked midhat to diagnose drama and she immediately pointed to",
    "borrowed midhat's neuro notes and still couldn't fix",
    "heard midhat memorize 200 drug names but forgot the existence of",
    "gave midhat a scalpel and she carved out the overconfidence of",
)


class SlapSection(types.StaticSection):
    verbs = types.ListAttribute("verbs", default=VERBS)
    """Verbs to choose from when slapping someone."""

    reflexive = types.ValidatedAttribute("reflexive", default="itself")
    """The reflexive pronoun the bot uses when someone slaps it."""

    pakistan_verbs = types.ListAttribute("pakistan_verbs", default=PAKISTAN_VERBS)


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

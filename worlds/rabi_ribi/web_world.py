from BaseClasses import Tutorial
from worlds.AutoWorld import WebWorld

class RabiRibiWeb(WebWorld):
    """Web integration for Rabi-Ribi"""
    tutorials = [Tutorial(
        "Multiworld Setup Guide",
        "A guide to setting up Rabi-Ribi integration for Archipelago multiworld games.",
        "English",
        "setup_en.md",
        "setup/en",
        ["PsyMarth", "Phie"]
    )]
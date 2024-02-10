"""This module represents item definitions for Rabi-Ribi"""
from BaseClasses import Item

class RabiRibiItem(Item):
    """Rabi Ribi Item Definition"""
    game: str = "Rabi-Ribi"

    @staticmethod
    def is_progression_item(name: str):
        """
        Defines if an item is considered a progression item.

        This will likely be updated as future logic changes happen.
        For now im porting the logic from the existing rando as is.
        """
        return name.startswith("Easter Egg") or name in set(
            "Fire Orb",
            "Water Orb",
            "Light Orb",
            "Piko Hammer",
            "Carrot Bomb",
            "Air Jump",
            "Rabi Slippers",
            "Sliding Powder",
            "Bunny Strike",
            "Wall Jump",
            "Air Dash",
            "Bunny Whirl",
            "Hammer Roll",
            "Carrot Shooter",
            "Charge Ring",
        )

item_table = {}

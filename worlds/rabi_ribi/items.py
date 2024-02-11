"""This module represents item definitions for Rabi-Ribi"""
from typing import List

from BaseClasses import Item
from .existing_randomizer.visualizer import load_item_locs

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
        return name in {
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
            "Easter Egg"
        }

def get_base_item_list() -> List[str]:
    """
    Get the base list of items in the game.
    No options are configurable at the moment.

    :returns List[str]: a list of item names to be added to the AP world. 
    """
    item_list = []

    # load list of all game items from existing randomizer.
    item_locs = load_item_locs()

    # Use a set amount of easter eggs
    for _ in range(5):
        item_list.append("Easter Egg")

    for item in item_locs.keys():
        # If we want to include the item, convert to the AP item id.
        # Otherwise, pass and dont include it.
        if item.startswith("ITEM_EGG"):
            pass
        elif item.startswith("ITEM_ATK_UP"):
            item_list.append("Attack Up")
        elif item.startswith("ITEM_HP_UP"):
            item_list.append("HP Up")
        elif item.startswith("ITEM_MP_UP"):
            item_list.append("MP Up")
        elif item.startswith("ITEM_PACK_UP"):
            item_list.append("Pack Up")
        elif item.startswith("ITEM_REGEN_UP"):
            item_list.append("Regen Up")
        elif item in [
            "ITEM_UNKNOWN_ITEM_1",
            "ITEM_UNKNOWN_ITEM_2",
            "ITEM_UNKNOWN_ITEM_3",
            "ITEM_P_HAIRPIN",
            "ITEM_SPEED_BOOST",
            "ITEM_BUNNY_STRIKE",
        ]:
            pass
        else:
            # Format the item string and then add to the item list
            item = item.split("_")
            item = " ".join(word.capitalize() for word in item[1:])
            item_list.append(item)

    return item_list

item_set = set(
    get_base_item_list()
)

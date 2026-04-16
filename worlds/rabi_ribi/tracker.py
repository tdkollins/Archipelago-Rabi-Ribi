from functools import cached_property
from typing import Any, Optional, override
from Options import Option
from worlds.AutoWorld import World
from .bases import RabiRibiWorldBase
from .constants import BASE_ID
from .names import ItemName

def should_regenerate_seed_for_universal_tracker(world: World):
    """
    If true, this world has information from Universal Tracker that should be used when generating the seed.
    This ensures that the world state matches the seed used by the connected server.
    """
    return hasattr(world.multiworld, "re_gen_passthrough") and world.game in world.multiworld.re_gen_passthrough # type: ignore

def map_page_index(data: Any) -> int:
    """
    Maps Rabi-Ribi area IDs to map IDs used by Poptracker.
    """
    if type(data) != int:
        return 0
    return data

MAP_OFFSETS = [
    (1, 2), # Southern Woodland
    (1, 3), # Western Coast
    (3, 3), # Island Core
    (2, 2), # Northern Tundra
    (1, 2), # Eastern Highlands
    (2, 0), # Rabi Rabi Town
    (1, 2), # Plurkwood
    (1, 2), # Subterranean Area
    (0, 5), # Warp Destination
    (1, 2), # System Interior
]

def location_icon_coords(index: int, coords: tuple[int, int]) -> Optional[tuple[int, int, str]]:
    """
    Maps a Rabi-Ribi room to coordinates on the Poptracker map.
    """
    if not coords or coords == (-1, -1):
        return None

    room_x, room_y = coords
    dx, dy = MAP_OFFSETS[index]
    x = ((room_x + dx) * 32) - 16
    y = ((room_y + dy) * 32) - 16
    return x, y, f"images/items/erina_badge.png"

# Maps AP location IDs to the respective names used by Poptracker
poptracker_name_mapping: dict[str, int] = {
    "Nature Orb/Nature Orb"                            : BASE_ID + 0x01,
    "Pack Up Forest Night/Pack Up"                     : BASE_ID + 0x02,
    "HP Up West Spectral/HP Up"                        : BASE_ID + 0x03,
    "Atk Up Forest Night/Atk Up"                       : BASE_ID + 0x04,
    "Pack Up Spectral/Pack Up"                         : BASE_ID + 0x05,
    "MP Up Cave/MP Up"                                 : BASE_ID + 0x06,
    "HP Up Cave/HP Up"                                 : BASE_ID + 0x07,
    "Toxic Strike/Toxic Strike"                        : BASE_ID + 0x08,
    "Piko Hammer/Piko Hammer"                          : BASE_ID + 0x09,
    "MP Up Forest Cave/MP Up"                          : BASE_ID + 0x0A,
    "Tough Skin/Tough Skin"                            : BASE_ID + 0x0B,
    "Regen Up Cave/Regen Up"                           : BASE_ID + 0x0C,
    "HP Up North Forest/HP Up"                         : BASE_ID + 0x0D,
    "Wall Jump/Wall Jump"                              : BASE_ID + 0x0E,
    "Regen Up Mid Forest/Regen Up"                     : BASE_ID + 0x0F,
    "MP Up Mid Spectral/MP Up"                         : BASE_ID + 0x10,
    "HP Up Mid Spectral/HP Up"                         : BASE_ID + 0x11,
    "Carrot Bomb/Carrot Bomb"                          : BASE_ID + 0x12,
    "Def Trade/Def Trade"                              : BASE_ID + 0x13,
    "Light Orb/Light Orb"                              : BASE_ID + 0x14,
    "HP Up Forest Post Cocoa/HP Up"                    : BASE_ID + 0x15,
    "Charge Ring/Charge Ring"                          : BASE_ID + 0x16,
    "Arm Strength/Arm Strength"                        : BASE_ID + 0x17,
    "Regen Up East Forest/Regen Up"                    : BASE_ID + 0x18,
    "Mana Wager/Mana Wager"                            : BASE_ID + 0x19,
    "MP Up East Forest/MP Up"                          : BASE_ID + 0x1A,
    "Pack Up East Forest/Pack Up"                      : BASE_ID + 0x1B,
    "MP Up Cicini/MP Up"                               : BASE_ID + 0x1C,
    "MP Up Northeast Forest/MP Up"                     : BASE_ID + 0x1D,
    "Survival/Survival"                                : BASE_ID + 0x1E,
    "Health Wager/Health Wager"                        : BASE_ID + 0x1F,
    "Atk Up Beach Cave/Atk Up"                         : BASE_ID + 0x20,
    "MP Up Graveyard Warp/MP Up"                       : BASE_ID + 0x21,
    "HP Up Graveyard/HP Up"                            : BASE_ID + 0x22,
    "Sunny Beam/Sunny Beam"                            : BASE_ID + 0x23,
    "MP Up Upper Graveyard/MP Up"                      : BASE_ID + 0x24,
    "Auto Earrings/Auto Earrings"                      : BASE_ID + 0x25,
    "Health Plus/Health Plus"                          : BASE_ID + 0x26,
    "MP Up Pyramid Dark Room/MP Up"                    : BASE_ID + 0x27,
    "Crisis Boost/Crisis Boost"                        : BASE_ID + 0x28,
    "Atk Up Graveyard/Atk Up"                          : BASE_ID + 0x29,
    "HP Up Inner Pyramid/HP Up"                        : BASE_ID + 0x2A,
    "HP Up Beach/HP Up"                                : BASE_ID + 0x2B,
    "Atk Up Pyramid/Atk Up"                            : BASE_ID + 0x2C,
    "Pack Up Pyramid/Pack Up"                          : BASE_ID + 0x2D,
    "Armored/Armored"                                  : BASE_ID + 0x2E,
    "Chaos Rod/Chaos Rod"                              : BASE_ID + 0x2F,
    "Pack Up Beach/Pack Up"                            : BASE_ID + 0x30,
    "Top Form/Top Form"                                : BASE_ID + 0x31,
    "HP Up Pyramid Entrance/HP Up"                     : BASE_ID + 0x32,
    "MP Up Pyramid Bomb Block Room/MP Up"              : BASE_ID + 0x33,
    "Air Dash/Air Dash"                                : BASE_ID + 0x34,
    "Regen Up Pyramid/Regen Up"                        : BASE_ID + 0x35,
    "Pure Love/Pure Love"                              : BASE_ID + 0x36,
    "MP Up Beach Tunnel/MP Up"                         : BASE_ID + 0x37,
    "Hourglass/Hourglass"                              : BASE_ID + 0x38,
    "HP Up Sky Island/HP Up"                           : BASE_ID + 0x39,
    "Pack Up Sky Island/Pack Up"                       : BASE_ID + 0x3A,
    "Regen Up Sky Island/Regen Up"                     : BASE_ID + 0x3B,
    "MP Up Beach Pillar/MP Up"                         : BASE_ID + 0x3C,
    "Def Grow/Def Grow"                                : BASE_ID + 0x3D,
    "Atk Up Park/Atk Up"                               : BASE_ID + 0x3E,
    "Atk Trade/Atk Trade"                              : BASE_ID + 0x3F,
    "HP Up Park/HP Up"                                 : BASE_ID + 0x40,
    "Rabi Slippers/Rabi Slippers"                      : BASE_ID + 0x41,
    "Regen Up Park/Regen Up"                           : BASE_ID + 0x42,
    "Health Surge/Health Surge"                        : BASE_ID + 0x43,
    "MP Up Sky Bridge/MP Up"                           : BASE_ID + 0x44,
    "MP Up UPRPRC HQ/MP Up"                            : BASE_ID + 0x45,
    "MP Up Park/MP Up"                                 : BASE_ID + 0x46,
    "Hex Cancel/Hex Cancel"                            : BASE_ID + 0x47,
    "HP Up Sky Bridge/HP Up"                           : BASE_ID + 0x48,
    "Pack Up Sky Bridge/Pack Up"                       : BASE_ID + 0x49,
    "Regen Up Sky Bridge/Regen Up"                     : BASE_ID + 0x4A,
    "Lucky Seven/Lucky Seven"                          : BASE_ID + 0x4B,
    "Atk Up Vanilla/Atk Up"                            : BASE_ID + 0x4C,
    "Hammer Wave/Hammer Wave"                          : BASE_ID + 0x4D,
    "Atk Up West Ravine/Atk Up"                        : BASE_ID + 0x4E,
    "HP Up South Ravine/HP Up"                         : BASE_ID + 0x4F,
    "Atk Up North Ravine/Atk Up"                       : BASE_ID + 0x50,
    "HP Up Mid Ravine/HP Up"                           : BASE_ID + 0x51,
    "MP Up Ravine/MP Up"                               : BASE_ID + 0x52,
    "Regen Up Ravine/Regen Up"                         : BASE_ID + 0x53,
    "Mana Surge/Mana Surge"                            : BASE_ID + 0x54,
    "HP Up Palace/HP Up"                               : BASE_ID + 0x55,
    "Water Orb/Water Orb"                              : BASE_ID + 0x56,
    "HP Up West Aquarium/HP Up"                        : BASE_ID + 0x57,
    "Mana Plus/Mana Plus"                              : BASE_ID + 0x58,
    "Atk Up Palace/Atk Up"                             : BASE_ID + 0x59,
    "Atk Up Snowland/Atk Up"                           : BASE_ID + 0x5A,
    "Regen Up Palace/Regen Up"                         : BASE_ID + 0x5B,
    "Stamina Plus/Stamina Plus"                        : BASE_ID + 0x5C,
    "MP Up Palace/MP Up"                               : BASE_ID + 0x5D,
    "Self Defense/Self Defense"                        : BASE_ID + 0x5E,
    "HP Up Upper Aquarium/HP Up"                       : BASE_ID + 0x5F,
    "Gold Carrot/Gold Carrot"                          : BASE_ID + 0x60,
    "Atk Up Upper Aquarium/Atk Up"                     : BASE_ID + 0x61,
    "Pack Up Icy Summit/Pack Up"                       : BASE_ID + 0x62,
    "Atk Up Icy Summit/Atk Up"                         : BASE_ID + 0x63,
    "Atk Up Mid Aquarium/Atk Up"                       : BASE_ID + 0x64,
    "MP Up Icy Summit/MP Up"                           : BASE_ID + 0x65,
    "MP Up Snowland/MP Up"                             : BASE_ID + 0x66,
    "Quick Barrette/Quick Barrette"                    : BASE_ID + 0x67,
    "HP Up Icy Summit/HP Up"                           : BASE_ID + 0x68,
    "Super Carrot/Super Carrot"                        : BASE_ID + 0x69,
    "Regen Up Snowland Water/Regen Up"                 : BASE_ID + 0x6A,
    "MP Up Aquarium/MP Up"                             : BASE_ID + 0x6B,
    "HP Up Snowland/HP Up"                             : BASE_ID + 0x6C,
    "Carrot Boost/Carrot Boost"                        : BASE_ID + 0x6D,
    "Regen Up Aquarium/Regen Up"                       : BASE_ID + 0x6E,
    "Pack Up Aquarium/Pack Up"                         : BASE_ID + 0x6F,
    "Regen Up Northwest Riverbank/Regen Up"            : BASE_ID + 0x70,
    "Pack Up Riverbank/Pack Up"                        : BASE_ID + 0x71,
    "MP Up Southwest Riverbank/MP Up"                  : BASE_ID + 0x72,
    "Atk Grow/Atk Grow"                                : BASE_ID + 0x73,
    "Regen Up South Riverbank/Regen Up"                : BASE_ID + 0x74,
    "Atk Up Riverbank Pit/Atk Up"                      : BASE_ID + 0x75,
    "Bunny Whirl/Bunny Whirl"                          : BASE_ID + 0x76,
    "Explode Shot/Explode Shot"                        : BASE_ID + 0x77,
    "MP Up Mid Riverbank/MP Up"                        : BASE_ID + 0x78,
    "Atk Up East Riverbank/Atk Up"                     : BASE_ID + 0x79,
    "Spike Barrier/Spike Barrier"                      : BASE_ID + 0x7A,
    "Frame Cancel/Frame Cancel"                        : BASE_ID + 0x7B,
    "HP Up Lab Slide Tunnel/HP Up"                     : BASE_ID + 0x7C,
    "MP Up Lab/MP Up"                                  : BASE_ID + 0x7D,
    "HP Up Riverbank/HP Up"                            : BASE_ID + 0x7E,
    "MP Up Evernight/MP Up"                            : BASE_ID + 0x7F,
    "HP Up Evernight/HP Up"                            : BASE_ID + 0x80,
    "HP Up Lab Pit/HP Up"                              : BASE_ID + 0x81,
    "Sliding Powder/Sliding Powder"                    : BASE_ID + 0x82,
    "Atk Up Evernight UPRPRC/Atk Up"                   : BASE_ID + 0x83,
    "Cashback/Cashback"                                : BASE_ID + 0x84,
    "Plus Necklace/Plus Necklace"                      : BASE_ID + 0x85,
    "Weaken/Weaken"                                    : BASE_ID + 0x86,
    "Atk Up Lab Computer/Atk Up"                       : BASE_ID + 0x87,
    "Pack Up South Evernight/Pack Up"                  : BASE_ID + 0x88,
    "Pack Up North Evernight/Pack Up"                  : BASE_ID + 0x89,
    "Regen Up Evernight/Regen Up"                      : BASE_ID + 0x8A,
    "Atk Up Evernight/Atk Up"                          : BASE_ID + 0x8B,
    "Atk Up East Lab/Atk Up"                           : BASE_ID + 0x8C,
    "Pack Up Lab/Pack Up"                              : BASE_ID + 0x8D,
    "Hammer Roll/Hammer Roll"                          : BASE_ID + 0x8E,
    "HP Up Volcanic/HP Up"                             : BASE_ID + 0x8F,
    "Fire Orb/Fire Orb"                                : BASE_ID + 0x90,
    "Pack Up Volcanic/Pack Up"                         : BASE_ID + 0x91,
    "Regen Up Cyberspace/Regen Up"                     : BASE_ID + 0x92,
    "Pack Up Cyberspace/Pack Up"                       : BASE_ID + 0x93,
    "Air Jump/Air Jump"                                : BASE_ID + 0x94,
    "HP Up Cyberspace/HP Up"                           : BASE_ID + 0x95,
    "Atk Up Cyberspace/Atk Up"                         : BASE_ID + 0x96,
    "MP Up Cyberspace/MP Up"                           : BASE_ID + 0x97,
    "P Hairpin/P Hairpin"                              : BASE_ID + 0x98,
    "Town Gift Items/Speed Boost"                      : BASE_ID + 0x99,
    "Town Gift Items/Bunny Strike"                     : BASE_ID + 0x9A,
    "Egg Forest Night Aruraune/Egg"                    : BASE_ID + 0x9B,
    "Egg Spectral West/Egg"                            : BASE_ID + 0x9C,
    "Egg Cave Under Hammer/Egg"                        : BASE_ID + 0x9D,
    "Egg Forest Night East/Egg"                        : BASE_ID + 0x9E,
    "Egg Spectral Slide/Egg"                           : BASE_ID + 0x9F,
    "Egg Cave Cocoa/Egg"                               : BASE_ID + 0xA0,
    "Egg Forest Northeast Ledge/Egg"                   : BASE_ID + 0xA1,
    "Egg Forest Northeast Pedestal/Egg"                : BASE_ID + 0xA2,
    "Egg Beach to Aquarium/Egg"                        : BASE_ID + 0xA3,
    "Egg Graveyard Near Library/Egg"                   : BASE_ID + 0xA4,
    "Egg Pyramid Beach/Egg"                            : BASE_ID + 0xA5,
    "Egg Pyramid Lower/Egg"                            : BASE_ID + 0xA6,
    "Egg Sky Town/Egg"                                 : BASE_ID + 0xA7,
    "Egg Park Spikes/Egg"                              : BASE_ID + 0xA8,
    "Egg Park Green Kotri/Egg"                         : BASE_ID + 0xA9,
    "Egg UPRPRC Base/Egg"                              : BASE_ID + 0xAA,
    "Egg Sky Bridge Warp/Egg"                          : BASE_ID + 0xAB,
    "Egg Sky Bridge by Vanilla/Egg"                    : BASE_ID + 0xAC,
    "Egg Ravine Above Chocolate/Egg"                   : BASE_ID + 0xAD,
    "Egg Ravine Mid/Egg"                               : BASE_ID + 0xAE,
    "Egg Snowland to Evernight/Egg"                    : BASE_ID + 0xAF,
    "Egg Palace Bridge/Egg"                            : BASE_ID + 0xB0,
    "Egg Aquarium/Egg"                                 : BASE_ID + 0xB1,
    "Egg Palace Wall/Egg"                              : BASE_ID + 0xB2,
    "Egg Snowland Warp/Egg"                            : BASE_ID + 0xB3,
    "Egg Icy Summit Nixie/Egg"                         : BASE_ID + 0xB4,
    "Egg Icy Summit Warp/Egg"                          : BASE_ID + 0xB5,
    "Egg Snowland Lake/Egg"                            : BASE_ID + 0xB6,
    "Egg Riverbank Spider Spike/Egg"                   : BASE_ID + 0xB7,
    "Egg Riverbank Wall/Egg"                           : BASE_ID + 0xB8,
    "Egg Lab/Egg"                                      : BASE_ID + 0xB9,
    "Egg Evernight Mid/Egg"                            : BASE_ID + 0xBA,
    "Egg Evernight Saya/Egg"                           : BASE_ID + 0xBB,
    "Egg Town/Egg"                                     : BASE_ID + 0xBC,
    "Egg Plurk Cats/Egg"                               : BASE_ID + 0xBD,
    "Egg Plurk Cave/Egg"                               : BASE_ID + 0xBE,
    "Egg Plurk East/Egg"                               : BASE_ID + 0xBF,
    "Egg Volcanic Bomb Bunnies/Egg"                    : BASE_ID + 0xC0,
    "Egg Volcanic Fire Orb/Egg"                        : BASE_ID + 0xC1,
    "Egg Volcanic Northeast/Egg"                       : BASE_ID + 0xC2,
    "Egg Volcanic Big Drop/Egg"                        : BASE_ID + 0xC3,
    "Egg Crespirit/Egg"                                : BASE_ID + 0xC4,
    "Egg System Interior/Egg"                          : BASE_ID + 0xC5,
    "Blessed/Blessed"                                  : BASE_ID + 0xC6,
    "Egg Rumi/Egg"                                     : BASE_ID + 0xC7,
    "Auto Trigger/Auto Trigger"                        : BASE_ID + 0xC8,
    "Hitbox Down/Hitbox Down"                          : BASE_ID + 0xC9,
    "Egg Library/Egg"                                  : BASE_ID + 0xCA,
    "Carrot Shooter/Carrot Shooter"                    : BASE_ID + 0xCB,
    "Egg Memories Sysint/Egg"                          : BASE_ID + 0xCC,
    "Egg Memories Ravine/Egg"                          : BASE_ID + 0xCD,
    "Egg Hospital Wall/Egg"                            : BASE_ID + 0xCE,
    "Egg Hospital Box/Egg"                             : BASE_ID + 0xCF,
    "Cyber Flower/Cyber Flower"                        : BASE_ID + 0xD0,
    "Egg System Interior 2/Egg"                        : BASE_ID + 0xD1,
    "Town Badges/Ribbon Badge"                         : BASE_ID + 0xD2,
    "Town Badges/Erina Badge"                          : BASE_ID + 0xD3,
    "Egg Halloween Cicini Room/Egg"                    : BASE_ID + 0xD4,
    "Egg Halloween West/Egg"                           : BASE_ID + 0xD5,
    "Egg Halloween Mid/Egg"                            : BASE_ID + 0xD6,
    "Egg Halloween Southwest Slide/Egg"                : BASE_ID + 0xD7,
    "Egg Halloween Near Boss/Egg"                      : BASE_ID + 0xD8,
    "Egg Halloween Warp Zone/Egg"                      : BASE_ID + 0xD9,
    "Egg Halloween Pillars/Egg Halloween Left Pillar"  : BASE_ID + 0xDA,
    "Egg Halloween Pillars/Egg Halloween Right Pillar" : BASE_ID + 0xDB,
    "Egg Halloween Past Pillars 1/Egg"                 : BASE_ID + 0xDC,
    "Egg Halloween Past Pillars 2/Egg"                 : BASE_ID + 0xDD,
    "PBPB Box/PBPB Box"                                : BASE_ID + 0xDE,
    "Egg Sky Bridge Above Warp/Egg"                    : BASE_ID + 0xDF,
    "Egg Snowland Spikes Room/Egg"                     : BASE_ID + 0xE0,
    "Egg Lab Entrance/Egg"                             : BASE_ID + 0xE1,
    "Egg Memories Cars Room/Egg"                       : BASE_ID + 0xE2,
    "Egg System Interior 2 Long Jump/Egg"              : BASE_ID + 0xE3,
}

class RabiRibiUTWorld(RabiRibiWorldBase):
    tracker_world = {
        "map_page_maps": ["maps/maps.jsonc"],
        "map_page_locations": ["locations/locations.jsonc"],
        "map_page_setting_key": "{player}_{team}_rabi_ribi_area_id",
        "map_page_index": map_page_index,
        "external_pack_key": "ut_pack_path",
        "location_setting_key": "{player}_{team}_rabi_ribi_coords",
        "location_icon_coords": location_icon_coords,
        "poptracker_name_mapping": poptracker_name_mapping
    }
    ut_can_gen_without_yaml = True
    glitches_item_name = ItemName.glitched_logic

    @cached_property
    def is_ut(self) -> bool:
        return getattr(self.multiworld, "generation_is_fake", False)

    @override
    def generate_early(self) -> None:
        re_gen_passthrough = getattr(self.multiworld, "re_gen_passthrough", {})
        if re_gen_passthrough and self.game in re_gen_passthrough:
            # Get the passed through slot data from the real generation
            slot_data: dict[str, Any] = re_gen_passthrough[self.game]
            slot_options: dict[str, Any] = slot_data.get("options", {})

            # Set all your options here instead of getting them from the YAML
            for key, value in slot_options.items():
                opt: Optional[Option] = getattr(self.options, key, None)
                if opt is not None:
                    # You can also set .value directly but that won't work if you have OptionSets
                    setattr(self.options, key, opt.from_any(value))

            self.picked_templates = slot_data["picked_templates"]
            self.map_transition_shuffle_order = slot_data["map_transition_shuffle_order"]
            self.start_location = slot_data["start_location"]

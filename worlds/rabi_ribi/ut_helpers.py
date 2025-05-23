from typing import Any, Dict, Optional, Tuple

from Options import Option
from worlds.AutoWorld import World
from .utility import rabi_ribi_base_id

def should_regenerate_seed_for_universal_tracker(world: World):
    """
    If true, this world has information from Universal Tracker that should be used when generating the seed.
    This ensures that the world state matches the seed used by the connected server.
    """
    return hasattr(world.multiworld, "re_gen_passthrough") and world.game in world.multiworld.re_gen_passthrough # type: ignore

def apply_options_from_slot_data_if_available(world: World):
    """
    Applies the options originally present in a player's YAML for use by Universal Tracker
    when regenerating the seed for tracking.
    """
    re_gen_passthrough = getattr(world.multiworld, "re_gen_passthrough", {})
    if re_gen_passthrough and world.game in re_gen_passthrough:
      # Get the passed through slot data from the real generation
      slot_data: dict[str, Any] = re_gen_passthrough[world.game]

      slot_options: dict[str, Any] = slot_data.get("options", {})
      # Set all your options here instead of getting them from the YAML
      for key, value in slot_options.items():
          opt: Optional[Option] = getattr(world.options, key, None)
          if opt is not None:
              # You can also set .value directly but that won't work if you have OptionSets
              setattr(world.options, key, opt.from_any(value))

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

def location_icon_coords(index: int, coords: Tuple[int, int]) -> Optional[Tuple[int, int, str]]:
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
poptracker_name_mapping: Dict[str, int] = {
    "Nature Orb/Nature Orb"                            : rabi_ribi_base_id + 0x01,
    "Pack Up Forest Night/Pack Up"                     : rabi_ribi_base_id + 0x02,
    "HP Up West Spectral/HP Up"                        : rabi_ribi_base_id + 0x03,
    "Atk Up Forest Night/Atk Up"                       : rabi_ribi_base_id + 0x04,
    "Pack Up Spectral/Pack Up"                         : rabi_ribi_base_id + 0x05,
    "MP Up Cave/MP Up"                                 : rabi_ribi_base_id + 0x06,
    "HP Up Cave/HP Up"                                 : rabi_ribi_base_id + 0x07,
    "Toxic Strike/Toxic Strike"                        : rabi_ribi_base_id + 0x08,
    "Piko Hammer/Piko Hammer"                          : rabi_ribi_base_id + 0x09,
    "MP Up Forest Cave/MP Up"                          : rabi_ribi_base_id + 0x0A,
    "Tough Skin/Tough Skin"                            : rabi_ribi_base_id + 0x0B,
    "Regen Up Cave/Regen Up"                           : rabi_ribi_base_id + 0x0C,
    "HP Up North Forest/HP Up"                         : rabi_ribi_base_id + 0x0D,
    "Wall Jump/Wall Jump"                              : rabi_ribi_base_id + 0x0E,
    "Regen Up Mid Forest/Regen Up"                     : rabi_ribi_base_id + 0x0F,
    "MP Up Mid Spectral/MP Up"                         : rabi_ribi_base_id + 0x10,
    "HP Up Mid Spectral/HP Up"                         : rabi_ribi_base_id + 0x11,
    "Carrot Bomb/Carrot Bomb"                          : rabi_ribi_base_id + 0x12,
    "Def Trade/Def Trade"                              : rabi_ribi_base_id + 0x13,
    "Light Orb/Light Orb"                              : rabi_ribi_base_id + 0x14,
    "HP Up Forest Post Cocoa/HP Up"                    : rabi_ribi_base_id + 0x15,
    "Charge Ring/Charge Ring"                          : rabi_ribi_base_id + 0x16,
    "Arm Strength/Arm Strength"                        : rabi_ribi_base_id + 0x17,
    "Regen Up East Forest/Regen Up"                    : rabi_ribi_base_id + 0x18,
    "Mana Wager/Mana Wager"                            : rabi_ribi_base_id + 0x19,
    "MP Up East Forest/MP Up"                          : rabi_ribi_base_id + 0x1A,
    "Pack Up East Forest/Pack Up"                      : rabi_ribi_base_id + 0x1B,
    "MP Up Cicini/MP Up"                               : rabi_ribi_base_id + 0x1C,
    "MP Up Northeast Forest/MP Up"                     : rabi_ribi_base_id + 0x1D,
    "Survival/Survival"                                : rabi_ribi_base_id + 0x1E,
    "Health Wager/Health Wager"                        : rabi_ribi_base_id + 0x1F,
    "Atk Up Beach Cave/Atk Up"                         : rabi_ribi_base_id + 0x20,
    "MP Up Graveyard Warp/MP Up"                       : rabi_ribi_base_id + 0x21,
    "HP Up Graveyard/HP Up"                            : rabi_ribi_base_id + 0x22,
    "Sunny Beam/Sunny Beam"                            : rabi_ribi_base_id + 0x23,
    "MP Up Upper Graveyard/MP Up"                      : rabi_ribi_base_id + 0x24,
    "Auto Earrings/Auto Earrings"                      : rabi_ribi_base_id + 0x25,
    "Health Plus/Health Plus"                          : rabi_ribi_base_id + 0x26,
    "MP Up Pyramid Dark Room/MP Up"                    : rabi_ribi_base_id + 0x27,
    "Crisis Boost/Crisis Boost"                        : rabi_ribi_base_id + 0x28,
    "Atk Up Graveyard/Atk Up"                          : rabi_ribi_base_id + 0x29,
    "HP Up Inner Pyramid/HP Up"                        : rabi_ribi_base_id + 0x2A,
    "HP Up Beach/HP Up"                                : rabi_ribi_base_id + 0x2B,
    "Atk Up Pyramid/Atk Up"                            : rabi_ribi_base_id + 0x2C,
    "Pack Up Pyramid/Pack Up"                          : rabi_ribi_base_id + 0x2D,
    "Armored/Armored"                                  : rabi_ribi_base_id + 0x2E,
    "Chaos Rod/Chaos Rod"                              : rabi_ribi_base_id + 0x2F,
    "Pack Up Beach/Pack Up"                            : rabi_ribi_base_id + 0x30,
    "Top Form/Top Form"                                : rabi_ribi_base_id + 0x31,
    "HP Up Pyramid Entrance/HP Up"                     : rabi_ribi_base_id + 0x32,
    "MP Up Pyramid Bomb Block Room/MP Up"              : rabi_ribi_base_id + 0x33,
    "Air Dash/Air Dash"                                : rabi_ribi_base_id + 0x34,
    "Regen Up Pyramid/Regen Up"                        : rabi_ribi_base_id + 0x35,
    "Pure Love/Pure Love"                              : rabi_ribi_base_id + 0x36,
    "MP Up Beach Tunnel/MP Up"                         : rabi_ribi_base_id + 0x37,
    "Hourglass/Hourglass"                              : rabi_ribi_base_id + 0x38,
    "HP Up Sky Island/HP Up"                           : rabi_ribi_base_id + 0x39,
    "Pack Up Sky Island/Pack Up"                       : rabi_ribi_base_id + 0x3A,
    "Regen Up Sky Island/Regen Up"                     : rabi_ribi_base_id + 0x3B,
    "MP Up Beach Pillar/MP Up"                         : rabi_ribi_base_id + 0x3C,
    "Def Grow/Def Grow"                                : rabi_ribi_base_id + 0x3D,
    "Atk Up Park/Atk Up"                               : rabi_ribi_base_id + 0x3E,
    "Atk Trade/Atk Trade"                              : rabi_ribi_base_id + 0x3F,
    "HP Up Park/HP Up"                                 : rabi_ribi_base_id + 0x40,
    "Rabi Slippers/Rabi Slippers"                      : rabi_ribi_base_id + 0x41,
    "Regen Up Park/Regen Up"                           : rabi_ribi_base_id + 0x42,
    "Health Surge/Health Surge"                        : rabi_ribi_base_id + 0x43,
    "MP Up Sky Bridge/MP Up"                           : rabi_ribi_base_id + 0x44,
    "MP Up UPRPRC HQ/MP Up"                            : rabi_ribi_base_id + 0x45,
    "MP Up Park/MP Up"                                 : rabi_ribi_base_id + 0x46,
    "Hex Cancel/Hex Cancel"                            : rabi_ribi_base_id + 0x47,
    "HP Up Sky Bridge/HP Up"                           : rabi_ribi_base_id + 0x48,
    "Pack Up Sky Bridge/Pack Up"                       : rabi_ribi_base_id + 0x49,
    "Regen Up Sky Bridge/Regen Up"                     : rabi_ribi_base_id + 0x4A,
    "Lucky Seven/Lucky Seven"                          : rabi_ribi_base_id + 0x4B,
    "Atk Up Vanilla/Atk Up"                            : rabi_ribi_base_id + 0x4C,
    "Hammer Wave/Hammer Wave"                          : rabi_ribi_base_id + 0x4D,
    "Atk Up West Ravine/Atk Up"                        : rabi_ribi_base_id + 0x4E,
    "HP Up South Ravine/HP Up"                         : rabi_ribi_base_id + 0x4F,
    "Atk Up North Ravine/Atk Up"                       : rabi_ribi_base_id + 0x50,
    "HP Up Mid Ravine/HP Up"                           : rabi_ribi_base_id + 0x51,
    "MP Up Ravine/MP Up"                               : rabi_ribi_base_id + 0x52,
    "Regen Up Ravine/Regen Up"                         : rabi_ribi_base_id + 0x53,
    "Mana Surge/Mana Surge"                            : rabi_ribi_base_id + 0x54,
    "HP Up Palace/HP Up"                               : rabi_ribi_base_id + 0x55,
    "Water Orb/Water Orb"                              : rabi_ribi_base_id + 0x56,
    "HP Up West Aquarium/HP Up"                        : rabi_ribi_base_id + 0x57,
    "Mana Plus/Mana Plus"                              : rabi_ribi_base_id + 0x58,
    "Atk Up Palace/Atk Up"                             : rabi_ribi_base_id + 0x59,
    "Atk Up Snowland/Atk Up"                           : rabi_ribi_base_id + 0x5A,
    "Regen Up Palace/Regen Up"                         : rabi_ribi_base_id + 0x5B,
    "Stamina Plus/Stamina Plus"                        : rabi_ribi_base_id + 0x5C,
    "MP Up Palace/MP Up"                               : rabi_ribi_base_id + 0x5D,
    "Self Defense/Self Defense"                        : rabi_ribi_base_id + 0x5E,
    "HP Up Upper Aquarium/HP Up"                       : rabi_ribi_base_id + 0x5F,
    "Gold Carrot/Gold Carrot"                          : rabi_ribi_base_id + 0x60,
    "Atk Up Upper Aquarium/Atk Up"                     : rabi_ribi_base_id + 0x61,
    "Pack Up Icy Summit/Pack Up"                       : rabi_ribi_base_id + 0x62,
    "Atk Up Icy Summit/Atk Up"                         : rabi_ribi_base_id + 0x63,
    "Atk Up Mid Aquarium/Atk Up"                       : rabi_ribi_base_id + 0x64,
    "MP Up Icy Summit/MP Up"                           : rabi_ribi_base_id + 0x65,
    "MP Up Snowland/MP Up"                             : rabi_ribi_base_id + 0x66,
    "Quick Barrette/Quick Barrette"                    : rabi_ribi_base_id + 0x67,
    "HP Up Icy Summit/HP Up"                           : rabi_ribi_base_id + 0x68,
    "Super Carrot/Super Carrot"                        : rabi_ribi_base_id + 0x69,
    "Regen Up Snowland Water/Regen Up"                 : rabi_ribi_base_id + 0x6A,
    "MP Up Aquarium/MP Up"                             : rabi_ribi_base_id + 0x6B,
    "HP Up Snowland/HP Up"                             : rabi_ribi_base_id + 0x6C,
    "Carrot Boost/Carrot Boost"                        : rabi_ribi_base_id + 0x6D,
    "Regen Up Aquarium/Regen Up"                       : rabi_ribi_base_id + 0x6E,
    "Pack Up Aquarium/Pack Up"                         : rabi_ribi_base_id + 0x6F,
    "Regen Up Northwest Riverbank/Regen Up"            : rabi_ribi_base_id + 0x70,
    "Pack Up Riverbank/Pack Up"                        : rabi_ribi_base_id + 0x71,
    "MP Up Southwest Riverbank/MP Up"                  : rabi_ribi_base_id + 0x72,
    "Atk Grow/Atk Grow"                                : rabi_ribi_base_id + 0x73,
    "Regen Up South Riverbank/Regen Up"                : rabi_ribi_base_id + 0x74,
    "Atk Up Riverbank Pit/Atk Up"                      : rabi_ribi_base_id + 0x75,
    "Bunny Whirl/Bunny Whirl"                          : rabi_ribi_base_id + 0x76,
    "Explode Shot/Explode Shot"                        : rabi_ribi_base_id + 0x77,
    "MP Up Mid Riverbank/MP Up"                        : rabi_ribi_base_id + 0x78,
    "Atk Up East Riverbank/Atk Up"                     : rabi_ribi_base_id + 0x79,
    "Spike Barrier/Spike Barrier"                      : rabi_ribi_base_id + 0x7A,
    "Frame Cancel/Frame Cancel"                        : rabi_ribi_base_id + 0x7B,
    "HP Up Lab Slide Tunnel/HP Up"                     : rabi_ribi_base_id + 0x7C,
    "MP Up Lab/MP Up"                                  : rabi_ribi_base_id + 0x7D,
    "HP Up Riverbank/HP Up"                            : rabi_ribi_base_id + 0x7E,
    "MP Up Evernight/MP Up"                            : rabi_ribi_base_id + 0x7F,
    "HP Up Evernight/HP Up"                            : rabi_ribi_base_id + 0x80,
    "HP Up Lab Pit/HP Up"                              : rabi_ribi_base_id + 0x81,
    "Sliding Powder/Sliding Powder"                    : rabi_ribi_base_id + 0x82,
    "Atk Up Evernight UPRPRC/Atk Up"                   : rabi_ribi_base_id + 0x83,
    "Cashback/Cashback"                                : rabi_ribi_base_id + 0x84,
    "Plus Necklace/Plus Necklace"                      : rabi_ribi_base_id + 0x85,
    "Weaken/Weaken"                                    : rabi_ribi_base_id + 0x86,
    "Atk Up Lab Computer/Atk Up"                       : rabi_ribi_base_id + 0x87,
    "Pack Up South Evernight/Pack Up"                  : rabi_ribi_base_id + 0x88,
    "Pack Up North Evernight/Pack Up"                  : rabi_ribi_base_id + 0x89,
    "Regen Up Evernight/Regen Up"                      : rabi_ribi_base_id + 0x8A,
    "Atk Up Evernight/Atk Up"                          : rabi_ribi_base_id + 0x8B,
    "Atk Up East Lab/Atk Up"                           : rabi_ribi_base_id + 0x8C,
    "Pack Up Lab/Pack Up"                              : rabi_ribi_base_id + 0x8D,
    "Hammer Roll/Hammer Roll"                          : rabi_ribi_base_id + 0x8E,
    "HP Up Volcanic/HP Up"                             : rabi_ribi_base_id + 0x8F,
    "Fire Orb/Fire Orb"                                : rabi_ribi_base_id + 0x90,
    "Pack Up Volcanic/Pack Up"                         : rabi_ribi_base_id + 0x91,
    "Regen Up Cyberspace/Regen Up"                     : rabi_ribi_base_id + 0x92,
    "Pack Up Cyberspace/Pack Up"                       : rabi_ribi_base_id + 0x93,
    "Air Jump/Air Jump"                                : rabi_ribi_base_id + 0x94,
    "HP Up Cyberspace/HP Up"                           : rabi_ribi_base_id + 0x95,
    "Atk Up Cyberspace/Atk Up"                         : rabi_ribi_base_id + 0x96,
    "MP Up Cyberspace/MP Up"                           : rabi_ribi_base_id + 0x97,
    "P Hairpin/P Hairpin"                              : rabi_ribi_base_id + 0x98,
    "Town Gift Items/Speed Boost"                      : rabi_ribi_base_id + 0x99,
    "Town Gift Items/Bunny Strike"                     : rabi_ribi_base_id + 0x9A,
    "Egg Forest Night Aruraune/Egg"                    : rabi_ribi_base_id + 0x9B,
    "Egg Spectral West/Egg"                            : rabi_ribi_base_id + 0x9C,
    "Egg Cave Under Hammer/Egg"                        : rabi_ribi_base_id + 0x9D,
    "Egg Forest Night East/Egg"                        : rabi_ribi_base_id + 0x9E,
    "Egg Spectral Slide/Egg"                           : rabi_ribi_base_id + 0x9F,
    "Egg Cave Cocoa/Egg"                               : rabi_ribi_base_id + 0xA0,
    "Egg Forest Northeast Ledge/Egg"                   : rabi_ribi_base_id + 0xA1,
    "Egg Forest Northeast Pedestal/Egg"                : rabi_ribi_base_id + 0xA2,
    "Egg Beach to Aquarium/Egg"                        : rabi_ribi_base_id + 0xA3,
    "Egg Graveyard Near Library/Egg"                   : rabi_ribi_base_id + 0xA4,
    "Egg Pyramid Beach/Egg"                            : rabi_ribi_base_id + 0xA5,
    "Egg Pyramid Lower/Egg"                            : rabi_ribi_base_id + 0xA6,
    "Egg Sky Town/Egg"                                 : rabi_ribi_base_id + 0xA7,
    "Egg Park Spikes/Egg"                              : rabi_ribi_base_id + 0xA8,
    "Egg Park Green Kotri/Egg"                         : rabi_ribi_base_id + 0xA9,
    "Egg UPRPRC Base/Egg"                              : rabi_ribi_base_id + 0xAA,
    "Egg Sky Bridge Warp/Egg"                          : rabi_ribi_base_id + 0xAB,
    "Egg Sky Bridge by Vanilla/Egg"                    : rabi_ribi_base_id + 0xAC,
    "Egg Ravine Above Chocolate/Egg"                   : rabi_ribi_base_id + 0xAD,
    "Egg Ravine Mid/Egg"                               : rabi_ribi_base_id + 0xAE,
    "Egg Snowland to Evernight/Egg"                    : rabi_ribi_base_id + 0xAF,
    "Egg Palace Bridge/Egg"                            : rabi_ribi_base_id + 0xB0,
    "Egg Aquarium/Egg"                                 : rabi_ribi_base_id + 0xB1,
    "Egg Palace Wall/Egg"                              : rabi_ribi_base_id + 0xB2,
    "Egg Snowland Warp/Egg"                            : rabi_ribi_base_id + 0xB3,
    "Egg Icy Summit Nixie/Egg"                         : rabi_ribi_base_id + 0xB4,
    "Egg Icy Summit Warp/Egg"                          : rabi_ribi_base_id + 0xB5,
    "Egg Snowland Lake/Egg"                            : rabi_ribi_base_id + 0xB6,
    "Egg Riverbank Spider Spike/Egg"                   : rabi_ribi_base_id + 0xB7,
    "Egg Riverbank Wall/Egg"                           : rabi_ribi_base_id + 0xB8,
    "Egg Lab/Egg"                                      : rabi_ribi_base_id + 0xB9,
    "Egg Evernight Mid/Egg"                            : rabi_ribi_base_id + 0xBA,
    "Egg Evernight Saya/Egg"                           : rabi_ribi_base_id + 0xBB,
    "Egg Town/Egg"                                     : rabi_ribi_base_id + 0xBC,
    "Egg Plurk Cats/Egg"                               : rabi_ribi_base_id + 0xBD,
    "Egg Plurk Cave/Egg"                               : rabi_ribi_base_id + 0xBE,
    "Egg Plurk East/Egg"                               : rabi_ribi_base_id + 0xBF,
    "Egg Volcanic Bomb Bunnies/Egg"                    : rabi_ribi_base_id + 0xC0,
    "Egg Volcanic Fire Orb/Egg"                        : rabi_ribi_base_id + 0xC1,
    "Egg Volcanic Northeast/Egg"                       : rabi_ribi_base_id + 0xC2,
    "Egg Volcanic Big Drop/Egg"                        : rabi_ribi_base_id + 0xC3,
    "Egg Crespirit/Egg"                                : rabi_ribi_base_id + 0xC4,
    "Egg System Interior/Egg"                          : rabi_ribi_base_id + 0xC5,
    "Blessed/Blessed"                                  : rabi_ribi_base_id + 0xC6,
    "Egg Rumi/Egg"                                     : rabi_ribi_base_id + 0xC7,
    "Auto Trigger/Auto Trigger"                        : rabi_ribi_base_id + 0xC8,
    "Hitbox Down/Hitbox Down"                          : rabi_ribi_base_id + 0xC9,
    "Egg Library/Egg"                                  : rabi_ribi_base_id + 0xCA,
    "Carrot Shooter/Carrot Shooter"                    : rabi_ribi_base_id + 0xCB,
    "Egg Memories Sysint/Egg"                          : rabi_ribi_base_id + 0xCC,
    "Egg Memories Ravine/Egg"                          : rabi_ribi_base_id + 0xCD,
    "Egg Hospital Wall/Egg"                            : rabi_ribi_base_id + 0xCE,
    "Egg Hospital Box/Egg"                             : rabi_ribi_base_id + 0xCF,
    "Cyber Flower/Cyber Flower"                        : rabi_ribi_base_id + 0xD0,
    "Egg System Interior 2/Egg"                        : rabi_ribi_base_id + 0xD1,
    "Town Badges/Ribbon Badge"                         : rabi_ribi_base_id + 0xD2,
    "Town Badges/Erina Badge"                          : rabi_ribi_base_id + 0xD3,
    "Egg Halloween Cicini Room/Egg"                    : rabi_ribi_base_id + 0xD4,
    "Egg Halloween West/Egg"                           : rabi_ribi_base_id + 0xD5,
    "Egg Halloween Mid/Egg"                            : rabi_ribi_base_id + 0xD6,
    "Egg Halloween Southwest Slide/Egg"                : rabi_ribi_base_id + 0xD7,
    "Egg Halloween Near Boss/Egg"                      : rabi_ribi_base_id + 0xD8,
    "Egg Halloween Warp Zone/Egg"                      : rabi_ribi_base_id + 0xD9,
    "Egg Halloween Pillars/Egg Halloween Left Pillar"  : rabi_ribi_base_id + 0xDA,
    "Egg Halloween Pillars/Egg Halloween Right Pillar" : rabi_ribi_base_id + 0xDB,
    "Egg Halloween Past Pillars 1/Egg"                 : rabi_ribi_base_id + 0xDC,
    "Egg Halloween Past Pillars 2/Egg"                 : rabi_ribi_base_id + 0xDD,
    "PBPB Box/PBPB Box"                                : rabi_ribi_base_id + 0xDE,
    "Egg Sky Bridge Above Warp/Egg"                    : rabi_ribi_base_id + 0xDF,
    "Egg Snowland Spikes Room/Egg"                     : rabi_ribi_base_id + 0xE0,
    "Egg Lab Entrance/Egg"                             : rabi_ribi_base_id + 0xE1,
    "Egg Memories Cars Room/Egg"                       : rabi_ribi_base_id + 0xE2,
    "Egg System Interior 2 Long Jump/Egg"              : rabi_ribi_base_id + 0xE3,
}

TRACKER_WORLD = {
    "map_page_maps": ["maps/maps.jsonc"],
    "map_page_locations": ["locations/locations.jsonc"],
    "map_page_setting_key": "{player}_{team}_rabi_ribi_area_id",
    "map_page_index": map_page_index,
    "external_pack_key": "ut_pack_path",
    "location_setting_key": "{player}_{team}_rabi_ribi_coords",
    "location_icon_coords": location_icon_coords,
    "poptracker_name_mapping": poptracker_name_mapping
}
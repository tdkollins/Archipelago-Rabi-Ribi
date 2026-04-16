"""This module represents location definitions for Rabi-Ribi"""
from BaseClasses import Location
from .options import RabiRibiOptions
from .names import LocationName
from .constants import GAME_NAME, BASE_ID

class RabiRibiLocation(Location):
    """Rabi Ribi Location Definition"""
    game: str = GAME_NAME

# Item Locations
southern_woodland_locations = {
    LocationName.nature_orb                   : BASE_ID + 0x01,
    LocationName.pack_up_forest_night         : BASE_ID + 0x02,
    LocationName.hp_up_west_spectral          : BASE_ID + 0x03,
    LocationName.atk_up_forest_night          : BASE_ID + 0x04,
    LocationName.pack_up_spectral             : BASE_ID + 0x05,
    LocationName.mp_up_cave                   : BASE_ID + 0x06,
    LocationName.hp_up_cave                   : BASE_ID + 0x07,
    LocationName.toxic_strike                 : BASE_ID + 0x08,
    LocationName.piko_hammer                  : BASE_ID + 0x09,
    LocationName.mp_up_forest_cave            : BASE_ID + 0x0A,
    LocationName.tough_skin                   : BASE_ID + 0x0B,
    LocationName.regen_up_cave                : BASE_ID + 0x0C,
    LocationName.hp_up_north_forest           : BASE_ID + 0x0D,
    LocationName.wall_jump                    : BASE_ID + 0x0E,
    LocationName.regen_up_mid_forest          : BASE_ID + 0x0F,
    LocationName.mp_up_mid_spectral           : BASE_ID + 0x10,
    LocationName.hp_up_mid_spectral           : BASE_ID + 0x11,
    LocationName.carrot_bomb                  : BASE_ID + 0x12,
    LocationName.def_trade                    : BASE_ID + 0x13,
    LocationName.light_orb                    : BASE_ID + 0x14,
    LocationName.hp_up_forest_post_cocoa      : BASE_ID + 0x15,
    LocationName.charge_ring                  : BASE_ID + 0x16,
    LocationName.arm_strength                 : BASE_ID + 0x17,
    LocationName.regen_up_east_forest         : BASE_ID + 0x18,
    LocationName.mana_wager                   : BASE_ID + 0x19,
    LocationName.mp_up_east_forest            : BASE_ID + 0x1A,
    LocationName.pack_up_east_forest          : BASE_ID + 0x1B,
    LocationName.mp_up_cicini                 : BASE_ID + 0x1C,
    LocationName.mp_up_northeast_forest       : BASE_ID + 0x1D,
}

western_coast_locations = {
    LocationName.survival                     : BASE_ID + 0x1E,
    LocationName.health_wager                 : BASE_ID + 0x1F,
    LocationName.atk_up_beach_cave            : BASE_ID + 0x20,
    LocationName.mp_up_graveyard_warp         : BASE_ID + 0x21,
    LocationName.hp_up_graveyard              : BASE_ID + 0x22,
    LocationName.sunny_beam                   : BASE_ID + 0x23,
    LocationName.mp_up_upper_graveyard        : BASE_ID + 0x24,
    LocationName.auto_earrings                : BASE_ID + 0x25,
    LocationName.health_plus                  : BASE_ID + 0x26,
    LocationName.mp_up_pyramid_dark_room      : BASE_ID + 0x27,
    LocationName.crisis_boost                 : BASE_ID + 0x28,
    LocationName.atk_up_graveyard             : BASE_ID + 0x29,
    LocationName.hp_up_inner_pyramid          : BASE_ID + 0x2A,
    LocationName.hp_up_beach                  : BASE_ID + 0x2B,
    LocationName.atk_up_pyramid               : BASE_ID + 0x2C,
    LocationName.pack_up_pyramid              : BASE_ID + 0x2D,
    LocationName.armored                      : BASE_ID + 0x2E,
    LocationName.chaos_rod                    : BASE_ID + 0x2F,
    LocationName.pack_up_beach                : BASE_ID + 0x30,
    LocationName.top_form                     : BASE_ID + 0x31,
    LocationName.hp_up_pyramid_entrance       : BASE_ID + 0x32,
    LocationName.mp_up_pyramid_bombblock_room : BASE_ID + 0x33,
    LocationName.air_dash                     : BASE_ID + 0x34,
    LocationName.regen_up_pyramid             : BASE_ID + 0x35,
    LocationName.pure_love                    : BASE_ID + 0x36,
    LocationName.mp_up_beach_tunnel           : BASE_ID + 0x37,
    LocationName.hourglass                    : BASE_ID + 0x38,
    LocationName.hp_up_sky_island             : BASE_ID + 0x39,
    LocationName.pack_up_sky_island           : BASE_ID + 0x3A,
    LocationName.regen_up_sky_island          : BASE_ID + 0x3B,
    LocationName.mp_up_beach_pillar           : BASE_ID + 0x3C,
}

island_core_locations = {
    LocationName.def_grow                     : BASE_ID + 0x3D,
    LocationName.atk_up_park                  : BASE_ID + 0x3E,
    LocationName.atk_trade                    : BASE_ID + 0x3F,
    LocationName.hp_up_park                   : BASE_ID + 0x40,
    LocationName.rabi_slippers                : BASE_ID + 0x41,
    LocationName.regen_up_park                : BASE_ID + 0x42,
    LocationName.health_surge                 : BASE_ID + 0x43,
    LocationName.mp_up_sky_bridge             : BASE_ID + 0x44,
    LocationName.mp_up_uprprc_hq              : BASE_ID + 0x45,
    LocationName.mp_up_park                   : BASE_ID + 0x46,
    LocationName.hex_cancel                   : BASE_ID + 0x47,
    LocationName.hp_up_sky_bridge             : BASE_ID + 0x48,
    LocationName.pack_up_sky_bridge           : BASE_ID + 0x49,
    LocationName.regen_up_sky_bridge          : BASE_ID + 0x4A,
    LocationName.lucky_seven                  : BASE_ID + 0x4B,
    LocationName.atk_up_vanilla               : BASE_ID + 0x4C,
    LocationName.hammer_wave                  : BASE_ID + 0x4D,
    LocationName.atk_up_west_ravine           : BASE_ID + 0x4E,
    LocationName.hp_up_south_ravine           : BASE_ID + 0x4F,
    LocationName.atk_up_north_ravine          : BASE_ID + 0x50,
    LocationName.hp_up_mid_ravine             : BASE_ID + 0x51,
    LocationName.mp_up_ravine                 : BASE_ID + 0x52,
    LocationName.regen_up_ravine              : BASE_ID + 0x53,
    LocationName.mana_surge                   : BASE_ID + 0x54,
}

northern_tundra_locations = {
    LocationName.hp_up_palace                 : BASE_ID + 0x55,
    LocationName.water_orb                    : BASE_ID + 0x56,
    LocationName.hp_up_west_aquarium          : BASE_ID + 0x57,
    LocationName.mana_plus                    : BASE_ID + 0x58,
    LocationName.atk_up_palace                : BASE_ID + 0x59,
    LocationName.atk_up_snowland              : BASE_ID + 0x5A,
    LocationName.regen_up_palace              : BASE_ID + 0x5B,
    LocationName.stamina_plus                 : BASE_ID + 0x5C,
    LocationName.mp_up_palace                 : BASE_ID + 0x5D,
    LocationName.self_defense                 : BASE_ID + 0x5E,
    LocationName.hp_up_upper_aquarium         : BASE_ID + 0x5F,
    LocationName.gold_carrot                  : BASE_ID + 0x60,
    LocationName.atk_up_upper_aquarium        : BASE_ID + 0x61,
    LocationName.pack_up_icy_summit           : BASE_ID + 0x62,
    LocationName.atk_up_icy_summit            : BASE_ID + 0x63,
    LocationName.atk_up_mid_aquarium          : BASE_ID + 0x64,
    LocationName.mp_up_icy_summit             : BASE_ID + 0x65,
    LocationName.mp_up_snowland               : BASE_ID + 0x66,
    LocationName.quick_barrette               : BASE_ID + 0x67,
    LocationName.hp_up_icy_summit             : BASE_ID + 0x68,
    LocationName.super_carrot                 : BASE_ID + 0x69,
    LocationName.regen_up_snowland_water      : BASE_ID + 0x6A,
    LocationName.mp_up_aquarium               : BASE_ID + 0x6B,
    LocationName.hp_up_snowland               : BASE_ID + 0x6C,
    LocationName.carrot_boost                 : BASE_ID + 0x6D,
    LocationName.regen_up_aquarium            : BASE_ID + 0x6E,
    LocationName.pack_up_aquarium             : BASE_ID + 0x6F,
}

eastern_highlands_locations = {
    LocationName.regen_up_northwest_riverbank : BASE_ID + 0x70,
    LocationName.pack_up_riverbank            : BASE_ID + 0x71,
    LocationName.mp_up_southwest_riverbank    : BASE_ID + 0x72,
    LocationName.atk_grow                     : BASE_ID + 0x73,
    LocationName.regen_up_south_riverbank     : BASE_ID + 0x74,
    LocationName.atk_up_riverbank_pit         : BASE_ID + 0x75,
    LocationName.bunny_whirl                  : BASE_ID + 0x76,
    LocationName.explode_shot                 : BASE_ID + 0x77,
    LocationName.mp_up_mid_riverbank          : BASE_ID + 0x78,
    LocationName.atk_up_east_riverbank        : BASE_ID + 0x79,
    LocationName.spike_barrier                : BASE_ID + 0x7A,
    LocationName.frame_cancel                 : BASE_ID + 0x7B,
    LocationName.hp_up_lab_slide_tunnel       : BASE_ID + 0x7C,
    LocationName.mp_up_lab                    : BASE_ID + 0x7D,
    LocationName.hp_up_riverbank              : BASE_ID + 0x7E,
    LocationName.mp_up_evernight              : BASE_ID + 0x7F,
    LocationName.hp_up_evernight              : BASE_ID + 0x80,
    LocationName.hp_up_lab_pit                : BASE_ID + 0x81,
    LocationName.sliding_powder               : BASE_ID + 0x82,
    LocationName.atk_up_evernight_uprprc      : BASE_ID + 0x83,
    LocationName.cashback                     : BASE_ID + 0x84,
    LocationName.plus_necklace                : BASE_ID + 0x85,
    LocationName.weaken                       : BASE_ID + 0x86,
    LocationName.atk_up_lab_computer          : BASE_ID + 0x87,
    LocationName.pack_up_south_evernight      : BASE_ID + 0x88,
    LocationName.pack_up_north_evernight      : BASE_ID + 0x89,
    LocationName.regen_up_evernight           : BASE_ID + 0x8A,
    LocationName.atk_up_evernight             : BASE_ID + 0x8B,
    LocationName.atk_up_east_lab              : BASE_ID + 0x8C,
    LocationName.pack_up_lab                  : BASE_ID + 0x8D,
    LocationName.hammer_roll                  : BASE_ID + 0x8E,

    LocationName.pbpb_box                     : BASE_ID + 0xDE,
}

subterranean_area_locations = {
    LocationName.hp_up_volcanic               : BASE_ID + 0x8F,
    LocationName.fire_orb                     : BASE_ID + 0x90,
    LocationName.pack_up_volcanic             : BASE_ID + 0x91,
}

system_interior_locations = {
    LocationName.regen_up_cyberspace          : BASE_ID + 0x92,
    LocationName.pack_up_cyberspace           : BASE_ID + 0x93,
    LocationName.air_jump                     : BASE_ID + 0x94,
    LocationName.hp_up_cyberspace             : BASE_ID + 0x95,
    LocationName.atk_up_cyberspace            : BASE_ID + 0x96,
    LocationName.mp_up_cyberspace             : BASE_ID + 0x97,
}

# Shufflable Gift Item Locations
shufflable_gift_item_plurkwood_locations = {
    LocationName.p_hairpin                    : BASE_ID + 0x98,
}

shufflable_gift_item_town_locations = {
    LocationName.speed_boost                  : BASE_ID + 0x99,
    LocationName.bunny_strike                 : BASE_ID + 0x9A,
}

# Egg Locations
southern_woodland_egg_locations = {
    LocationName.egg_forestnight_aruraune     : BASE_ID + 0x9B,
    LocationName.egg_spectral_west            : BASE_ID + 0x9C,
    LocationName.egg_cave_under_hammer        : BASE_ID + 0x9D,
    LocationName.egg_forestnight_east         : BASE_ID + 0x9E,
    LocationName.egg_spectral_slide           : BASE_ID + 0x9F,
    LocationName.egg_cave_cocoa               : BASE_ID + 0xA0,
    LocationName.egg_forest_ne_ledge          : BASE_ID + 0xA1,
    LocationName.egg_forest_ne_pedestal       : BASE_ID + 0xA2,
}

western_coast_egg_locations = {
    LocationName.egg_beach_to_aquarium        : BASE_ID + 0xA3,
    LocationName.egg_graveyard_near_library   : BASE_ID + 0xA4,
    LocationName.egg_pyramid_beach            : BASE_ID + 0xA5,
    LocationName.egg_pyramid_lower            : BASE_ID + 0xA6,
    LocationName.egg_sky_town                 : BASE_ID + 0xA7,
}

island_core_egg_locations = {
    LocationName.egg_park_spikes              : BASE_ID + 0xA8,
    LocationName.egg_park_green_kotri         : BASE_ID + 0xA9,
    LocationName.egg_uprprc_base              : BASE_ID + 0xAA,
    LocationName.egg_sky_bridge_warp          : BASE_ID + 0xAB,
    LocationName.egg_sky_bridge_by_vanilla    : BASE_ID + 0xAC,
    LocationName.egg_ravine_above_chocolate   : BASE_ID + 0xAD,
    LocationName.egg_ravine_mid               : BASE_ID + 0xAE,

    LocationName.egg_sky_bridge_above_warp    : BASE_ID + 0xDF,
}

northern_tundra_egg_locations = {
    LocationName.egg_snowland_to_evernight    : BASE_ID + 0xAF,
    LocationName.egg_palace_bridge            : BASE_ID + 0xB0,
    LocationName.egg_aquarium                 : BASE_ID + 0xB1,
    LocationName.egg_palace_wall              : BASE_ID + 0xB2,
    LocationName.egg_snowland_warp            : BASE_ID + 0xB3,
    LocationName.egg_icy_summit_nixie         : BASE_ID + 0xB4,
    LocationName.egg_icy_summit_warp          : BASE_ID + 0xB5,
    LocationName.egg_snowland_lake            : BASE_ID + 0xB6,

    LocationName.egg_snowland_spikes_room     : BASE_ID + 0xE0,
}

eastern_highlands_egg_locations = {
    LocationName.egg_riverbank_spider_spike   : BASE_ID + 0xB7,
    LocationName.egg_riverbank_wall           : BASE_ID + 0xB8,
    LocationName.egg_lab                      : BASE_ID + 0xB9,
    LocationName.egg_evernight_mid            : BASE_ID + 0xBA,
    LocationName.egg_evernight_saya           : BASE_ID + 0xBB,

    LocationName.egg_lab_entrance             : BASE_ID + 0xE1,
}

rabi_rabi_town_egg_locations = {
    LocationName.egg_town                     : BASE_ID + 0xBC,
}

plurkwood_egg_locations = {
    LocationName.egg_plurk_cats               : BASE_ID + 0xBD,
    LocationName.egg_plurk_cave               : BASE_ID + 0xBE,
    LocationName.egg_plurk_east               : BASE_ID + 0xBF,
}

subterranean_area_egg_locations = {
    LocationName.egg_volcanic_bomb_bunnies    : BASE_ID + 0xC0,
    LocationName.egg_volcanic_fire_orb        : BASE_ID + 0xC1,
    LocationName.egg_volcanic_ne              : BASE_ID + 0xC2,
    LocationName.egg_volcanic_big_drop        : BASE_ID + 0xC3,
}

warp_destination_egg_locations = {
    LocationName.egg_crespirit                : BASE_ID + 0xC4,
}

system_interior_egg_locations = {
    LocationName.egg_sysint1                  : BASE_ID + 0xC5,
}

# Post Game Locations
southern_woodland_post_game_locations = {
    LocationName.blessed                      : BASE_ID + 0xC6,
    LocationName.egg_rumi                     : BASE_ID + 0xC7,
}

western_coast_post_game_locations = {
    LocationName.auto_trigger                 : BASE_ID + 0xC8,
    LocationName.hitbox_down                  : BASE_ID + 0xC9,
    LocationName.egg_library                  : BASE_ID + 0xCA,
}

subterranean_area_post_game_locations = {
    LocationName.carrot_shooter               : BASE_ID + 0xCB,
    LocationName.egg_memories_sysint          : BASE_ID + 0xCC,
    LocationName.egg_memories_ravine          : BASE_ID + 0xCD,

    LocationName.egg_memories_cars_room       : BASE_ID + 0xE2,
}

warp_destination_post_game_locations = {
    LocationName.egg_hospital_wall            : BASE_ID + 0xCE,
    LocationName.egg_hospital_box             : BASE_ID + 0xCF,
}

system_interior_post_game_locations = {
    LocationName.cyber_flower                 : BASE_ID + 0xD0,
    LocationName.egg_sysint2                  : BASE_ID + 0xD1,

    LocationName.egg_sysint2_long_jump        : BASE_ID + 0xE3
}

# Post Irisu Locations
rabi_rabi_town_post_irisu_locations = {
    LocationName.ribbon_badge                 : BASE_ID + 0xD2,
    LocationName.erina_badge                  : BASE_ID + 0xD3,
}

# Halloween Locations
western_coast_halloween_locations = {
    LocationName.egg_halloween_cicini_room    : BASE_ID + 0xD4,
    LocationName.egg_halloween_west           : BASE_ID + 0xD5,
    LocationName.egg_halloween_mid            : BASE_ID + 0xD6,
    LocationName.egg_halloween_sw_slide       : BASE_ID + 0xD7,
    LocationName.egg_halloween_near_boss      : BASE_ID + 0xD8,
    LocationName.egg_halloween_warp_zone      : BASE_ID + 0xD9,
    LocationName.egg_halloween_left_pillar    : BASE_ID + 0xDA,
    LocationName.egg_halloween_right_pillar   : BASE_ID + 0xDB,
    LocationName.egg_halloween_past_pillars1  : BASE_ID + 0xDC,
    LocationName.egg_halloween_past_pillars2  : BASE_ID + 0xDD,
}

# Area Location Tables
southern_woodland_table = {
    **southern_woodland_locations,
    **southern_woodland_egg_locations,
    **southern_woodland_post_game_locations,
}

western_coast_table = {
    **western_coast_locations,
    **western_coast_egg_locations,
    **western_coast_post_game_locations,
    **western_coast_halloween_locations,
}

island_core_table = {
    **island_core_locations,
    **island_core_egg_locations,
}

northern_tundra_table = {
    **northern_tundra_locations,
    **northern_tundra_egg_locations,
}

eastern_highlands_table = {
    **eastern_highlands_locations,
    **eastern_highlands_egg_locations,
}

rabi_rabi_town_table = {
    **rabi_rabi_town_egg_locations,
    **rabi_rabi_town_post_irisu_locations
}

plurkwood_table = {
    **plurkwood_egg_locations,
}

subterranean_area_table = {
    **subterranean_area_locations,
    **subterranean_area_egg_locations,
    **subterranean_area_post_game_locations,
}

warp_destination_table = {
    **warp_destination_egg_locations,
    **warp_destination_post_game_locations
}

system_interior_table = {
    **system_interior_locations,
    **system_interior_egg_locations,
    **system_interior_post_game_locations
}

shufflable_gift_item_table = {
    **shufflable_gift_item_town_locations,
    **shufflable_gift_item_plurkwood_locations
}

# Combined Location Table
all_locations = {
    **southern_woodland_table,
    **western_coast_table,
    **island_core_table,
    **northern_tundra_table,
    **eastern_highlands_table,
    **rabi_rabi_town_table,
    **plurkwood_table,
    **subterranean_area_table,
    **warp_destination_table,
    **system_interior_table,
    **shufflable_gift_item_table
}

default_locations = {
    **southern_woodland_locations,
    **southern_woodland_egg_locations,
    **western_coast_locations,
    **western_coast_egg_locations,
    **island_core_locations,
    **island_core_egg_locations,
    **northern_tundra_locations,
    **northern_tundra_egg_locations,
    **eastern_highlands_locations,
    **eastern_highlands_egg_locations,
    **shufflable_gift_item_town_locations,
    **rabi_rabi_town_egg_locations,
    **subterranean_area_locations,
    **subterranean_area_egg_locations,
    **system_interior_locations,
    **system_interior_egg_locations,
}

lookup_location_id_to_name = {code: name for name, code in all_locations.items()}

location_groups = {
    LocationName.southern_woodland_region   : set(southern_woodland_table.keys()),
    LocationName.western_coast_region       : set(western_coast_table.keys()),
    LocationName.island_core_region         : set(island_core_table.keys()),
    LocationName.northern_tundra_region     : set(northern_tundra_table.keys()),
    LocationName.eastern_highlands_region   : set(eastern_highlands_table.keys()),
    LocationName.rabi_rabi_town_region      : set(rabi_rabi_town_table.keys()),
    LocationName.plurkwood_region           : set(plurkwood_table.keys()),
    LocationName.subterranean_area_region   : set(subterranean_area_table.keys()),
    LocationName.system_interior_region     : set(system_interior_table.keys()),
    LocationName.shufflable_gift_items      : set(shufflable_gift_item_table.keys())
}

def setup_locations(options: RabiRibiOptions):
    location_table: dict[str, int] = {
        **default_locations
    }

    if options.include_plurkwood:
        location_table.update(**shufflable_gift_item_plurkwood_locations)
        location_table.update(**plurkwood_egg_locations)

    if options.include_warp_destination:
        location_table.update(**warp_destination_egg_locations)
        if options.include_post_game:
            location_table.update(**warp_destination_post_game_locations)
    
    if options.include_post_game:
        location_table.update(**southern_woodland_post_game_locations)
        location_table.update(**western_coast_post_game_locations)
        location_table.update(**subterranean_area_post_game_locations)
        location_table.update(**system_interior_post_game_locations)

    if options.include_post_irisu:
        location_table.update(**rabi_rabi_town_post_irisu_locations)

    if options.include_halloween:
        location_table.update(**western_coast_halloween_locations)

    return location_table

import argparse, random, sys
from . import mapfileio
from . import musicrandomizer
from . import backgroundrandomizer
from . import versioncheck
from .utility import *
from .generator import Generator
from .dataparser import RandomizerData
from .converter import diffgenerator as diffgenerator

def parse_args():
    args = argparse.ArgumentParser(description='Rabi-Ribi Randomizer - %s' % versioncheck.VERSION_STRING)
    args.add_argument('--version', action='store_true', help='Print Randomizer Version')
    args.add_argument('-source-dir', default='original_maps', help='Source directory for original maps. Defaults to original_maps/. Do not make the source dir the output dir.')
    args.add_argument('-output-dir', default='generated_maps', help='Output directory for generated maps. Defaults to generated_maps/. Do not make the source dir the output dir.')
    args.add_argument('-config-file', default='existing_randomizer/config.txt', help='Config file to use')
    args.add_argument('-seed', default=None, type=str, help='Random seed')
    args.add_argument('--no-write', action='store_true', help='Flag to disable map generation, and do only map analysis')
    args.add_argument('--no-fixes', dest='apply_fixes', default=True, action='store_false', help='Flag to disable randomizer-specific map fixes')
    args.add_argument('--reset', action='store_true', help='Reset maps by copying the original maps to the output directory.')
    args.add_argument('--hash', action='store_true', help='Generate a hash of the maps in the output directory.')
    args.add_argument('--check-for-updates', action='store_true', help='Check for the latest version of randomizer.')
    args.add_argument('--check-branch', action='store_true', help='Displays which branch the randomizer is currently on (D or M).')
    args.add_argument('--shuffle-music', action='store_true', help='Shuffles the music in the map.')
    args.add_argument('--shuffle-backgrounds', action='store_true', help='Shuffles the backgrounds in the map.')
    args.add_argument('--shuffle-map-transitions', action='store_true', help='Shuffles map transitions between maps.')
    args.add_argument('--shuffle-gift-items', action='store_true', help='Shuffles certain gift items in the maps.')
    args.add_argument('--shuffle-start-location', action='store_true', help='Shuffle start area.')
    args.add_argument('-constraint-changes', default=0, type=float, help='Average number of changed map constraints')
    args.add_argument('-min-constraint-changes', default=-1, type=float, help='Min number of changed map constraints')
    args.add_argument('-max-constraint-changes', default=-1, type=float, help='Max number of changed map constraints')
    args.add_argument('-apply-beginner-mod', action='store_true', help='Apply beginner mod')
    args.add_argument('--no-laggy-backgrounds', action='store_true', help='Don\'t include laggy backgrounds in background shuffle.')
    args.add_argument('--no-difficult-backgrounds', action='store_true', help='Don\'t include backgrounds in background shuffle that interfere with visibility.')
    args.add_argument('--super-attack-mode', action='store_true', help='Start the game with a bunch of attack ups, so you do lots more damage.')
    args.add_argument('--hyper-attack-mode', action='store_true', help='Like Super Attack Mode, but with 35 attack ups.')
    args.add_argument('--open-mode', action='store_true', help='Removes prologue triggers that restrict exploration.')
    #args.add_argument('--hide-unreachable', action='store_true', help='Hide list of unreachable items. Affects seed.')
    args.add_argument('--hide-difficulty', action='store_true', help='Hide difficulty rating. Affects seed.')
    args.add_argument('-min-chain-length', default=0, type=int, help='Set a minimum chain length for generation. Faster tham -min-difficulty.')
    args.add_argument('-min-difficulty', default=0, type=float, help='Set a minimum difficulty for generation. Slower tham -min-chain-length.')
    args.add_argument('-max-sequence-breakability', default=None, type=float, help='Set a maximum seed breakability for generation. Slower tham -min-chain-length.')
    args.add_argument('-max-attempts', default=1000, type=int, help='Set the maximum amount of seed generation attempts before giving up. Default is 1000.')
    args.add_argument('--egg-goals', action='store_true', help='Egg goals mode. Hard-to-reach items are replaced with easter eggs. All other eggs are removed from the map.')
    args.add_argument('-extra-eggs', default=0, type=int, help='Number of extra randomly-chosen eggs for egg-goals mode (in addition to the hard-to-reach eggs)')
    args.add_argument('-num-hard-to-reach', default=5, type=int, help='Number of hard to reach items/eggs. Default is 5.')
    args.add_argument('--debug-visualize', action='store_true', help='Output debug info and node graph image.')

    # AP Change: Don't pass args from generation, as they're for Archipelago
    return args.parse_args([])


def apply_item_specific_fixes(mod, allocation):
    item_at_location = allocation.item_at_item_location

    # AP Change: Added more robust method for checking if a location
    #            an egg, as the location may not exist in AP.
    def is_egg_at_location(location_name):
        return location_name in item_at_location \
            and is_egg(item_at_location[location_name])

    if is_egg_at_location('PURE_LOVE'):
        data = mod.stored_datas[1]
        data.tiledata_event[xy_to_index(404,12)] = 3

    if is_egg_at_location('ATK_UP_SNOWLAND'):
        data = mod.stored_datas[3]
        data.tiledata_event[xy_to_index(93,119)] = 3

    if is_egg_at_location('HP_UP_NORTH_FOREST'):
        data = mod.stored_datas[0]
        data.tiledata_map[xy_to_index(271,51)] = 0
        data.tiledata_tiles1[xy_to_index(271,51)] = 0

    if is_egg_at_location('EGG_HOSPITAL_BOX'):
        data = mod.stored_datas[8]
        data.tiledata_map[xy_to_index(486,73)] = 0
        data.tiledata_tiles1[xy_to_index(486,73)] = 0

    if is_egg_at_location('EGG_HOSPITAL_WALL'):
        data = mod.stored_datas[8]
        data.tiledata_map[xy_to_index(438,64)] = 0
        data.tiledata_tiles1[xy_to_index(438,64)] = 0


def apply_fixes_for_randomizer(areaid, data):
    """
    AP Changes:
        Remove Forest Night UPRPRC Fight
    """
    if areaid == 0:
        # Remove save point and autosave point before Cocoa1
        for y in range(84,88):
            data.tiledata_event[xy_to_index(358,y)] = 0
            data.tiledata_event[xy_to_index(363,y)] = 0
            data.tiledata_event[xy_to_index(364,y)] = 0
        for y in range(85,88):
            data.tiledata_event[xy_to_index(361,y)] = 0
            data.tiledata_event[xy_to_index(365,y)] = 0

        # Add autosave point at ledge above Cocoa1
        data.tiledata_event[xy_to_index(378,80)] = 42
        data.tiledata_event[xy_to_index(378,81)] = 42
        data.tiledata_event[xy_to_index(380,80)] = 44
        data.tiledata_event[xy_to_index(380,81)] = 44
        data.tiledata_event[xy_to_index(376,80)] = 44
        data.tiledata_event[xy_to_index(376,81)] = 44
        data.tiledata_event[xy_to_index(376,82)] = 44

        # Remove east starting forest lock
        for y in range(102,108):
            data.tiledata_event[xy_to_index(358,y)] = 0

        # Remove Forest Night UPRPRC Fight
        for y in range(70,75):
            data.tiledata_event[xy_to_index(173,y)] = 0

    if areaid == 1:
        # Remove trampoline at crisis boost location
        data.tiledata_event[xy_to_index(246,63)] = 0
        data.tiledata_event[xy_to_index(246,64)] = 0

        # Remove autosave point at chaos rod
        for y in range(182,189):
            data.tiledata_event[xy_to_index(314,y)] = 0
        for y in range(182,188):
            data.tiledata_event[xy_to_index(312,y)] = 0
        data.tiledata_event[xy_to_index(316,188)] = 0

        # Remove autosave point at air dash
        for y in range(47,55):
            data.tiledata_event[xy_to_index(387,y)] = 0

    if areaid == 4:
        # Remove save point at slide location in lab
        for y in range(185,189):
            data.tiledata_event[xy_to_index(309,y)] = 0
        for y in range(186,189):
            data.tiledata_event[xy_to_index(310,y)] = 0

    if areaid == 6:
        # Add EV_NOEVENT0 at plurk warp stone
        data.tiledata_event[xy_to_index(188,38)] = 524

    if areaid == 7:
        # Remove redundant map transition
        for y in range(37,43):
            for x in range(96,101):
                data.tiledata_event[xy_to_index(x,y)] = 0

#    if areaid == 8:
#        # Remove autosaves from warp destination
#        data.tiledata_event = [0 if x==42 else x for x in data.tiledata_event]


def apply_open_mode_fixes(areaid, data):
    # Prologue triggers that prevent you from getting past many areas
    data.tiledata_event = [0 if x==300 else x for x in data.tiledata_event]

    if areaid == 0:
        # Trigger blocking going to beach from start
        data.tiledata_event = [0 if x==301 else x for x in data.tiledata_event]


def apply_post_game_fixes(areaid, data):
    # library
    if areaid == 1:
        # entrance
        for x in range(281, 286):
            data.tiledata_map[xy_to_index(x, 64)] = 0
            data.tiledata_tiles1[xy_to_index(x, 64)] = 0
            data.tiledata_event[xy_to_index(x, 64)] = 0
        for x in range(295, 302):
            data.tiledata_map[xy_to_index(x, 61)] = 0
            data.tiledata_tiles1[xy_to_index(x, 61)] = 0
            data.tiledata_event[xy_to_index(x, 61)] = 0

        # lower area and hitbox down
        data.tiledata_map[xy_to_index(352, 51)] = 0
        data.tiledata_tiles1[xy_to_index(352, 51)] = 0
        data.tiledata_event[xy_to_index(352, 51)] = 0

        data.tiledata_event[xy_to_index(354, 61)] = 0
        data.tiledata_event[xy_to_index(354, 62)] = 0

        data.tiledata_event[xy_to_index(376, 63)] = 0
        data.tiledata_event[xy_to_index(376, 64)] = 0

        data.tiledata_event[xy_to_index(359, 34)] = 0
        data.tiledata_event[xy_to_index(359, 35)] = 0

        data.tiledata_event[xy_to_index(343, 40)] = 0
        data.tiledata_event[xy_to_index(343, 40)] = 0

        # large gaps to mid lower area
        for x in range(327, 330):
            data.tiledata_map[xy_to_index(x, 48)] = 0
            data.tiledata_tiles1[xy_to_index(x, 48)] = 0
            data.tiledata_event[xy_to_index(x, 48)] = 0

        data.tiledata_event[xy_to_index(334, 52)] = 0
        data.tiledata_event[xy_to_index(334, 53)] = 0

        for x in range(303, 305):
            data.tiledata_map[xy_to_index(x, 39)] = 0
            data.tiledata_tiles1[xy_to_index(x, 39)] = 0
            data.tiledata_event[xy_to_index(x, 39)] = 0
        for y in range(38, 40):
            data.tiledata_map[xy_to_index(308, y)] = 0
            data.tiledata_tiles1[xy_to_index(308, y)] = 0
            data.tiledata_event[xy_to_index(308, y)] = 0
        for y in range(35, 43):
            data.tiledata_map[xy_to_index(312, y)] = 0
            data.tiledata_tiles1[xy_to_index(312, y)] = 0
            data.tiledata_event[xy_to_index(312, y)] = 0

        data.tiledata_event[xy_to_index(310, 49)] = 0
        data.tiledata_event[xy_to_index(310, 50)] = 0

        # library zip and 8 tile walljump room
        data.tiledata_map[xy_to_index(223, 31)] = 0
        data.tiledata_tiles1[xy_to_index(223, 31)] = 0
        data.tiledata_event[xy_to_index(223, 31)] = 0

        data.tiledata_map[xy_to_index(232, 34)] = 0
        data.tiledata_tiles1[xy_to_index(232, 34)] = 0
        data.tiledata_event[xy_to_index(232, 34)] = 0

        data.tiledata_map[xy_to_index(235, 42)] = 0
        data.tiledata_tiles1[xy_to_index(235, 42)] = 0
        data.tiledata_event[xy_to_index(235, 42)] = 0

        data.tiledata_map[xy_to_index(236, 36)] = 0
        data.tiledata_tiles1[xy_to_index(236, 36)] = 0
        data.tiledata_event[xy_to_index(236, 36)] = 0

        data.tiledata_map[xy_to_index(231, 27)] = 0
        data.tiledata_tiles1[xy_to_index(231, 27)] = 0
        data.tiledata_event[xy_to_index(231, 27)] = 0

        for x in range(224, 231):
            data.tiledata_map[xy_to_index(x, 42)] = 0
            data.tiledata_tiles1[xy_to_index(x, 42)] = 0
            data.tiledata_event[xy_to_index(x, 42)] = 0

        # beneath auto trigger
        for x in range(293, 297):
            data.tiledata_map[xy_to_index(x, 31)] = 0
            data.tiledata_tiles1[xy_to_index(x, 31)] = 0
            data.tiledata_event[xy_to_index(x, 31)] = 0

        data.tiledata_event[xy_to_index(291, 32)] = 0
        data.tiledata_event[xy_to_index(291, 33)] = 0

        data.tiledata_event[xy_to_index(297, 30)] = 0
        data.tiledata_event[xy_to_index(297, 31)] = 0

        # mid upper to irisu
        data.tiledata_map[xy_to_index(330, 30)] = 0
        data.tiledata_tiles1[xy_to_index(330, 30)] = 0
        data.tiledata_event[xy_to_index(330, 30)] = 0

        data.tiledata_map[xy_to_index(335, 27)] = 0
        data.tiledata_tiles1[xy_to_index(335, 27)] = 0
        data.tiledata_event[xy_to_index(335, 27)] = 0

        data.tiledata_map[xy_to_index(336, 24)] = 0
        data.tiledata_tiles1[xy_to_index(336, 24)] = 0
        data.tiledata_event[xy_to_index(336, 24)] = 0

        data.tiledata_map[xy_to_index(337, 21)] = 0
        data.tiledata_tiles1[xy_to_index(337, 21)] = 0
        data.tiledata_event[xy_to_index(337, 21)] = 0

        data.tiledata_event[xy_to_index(327, 30)] = 0
        data.tiledata_event[xy_to_index(327, 31)] = 0

        data.tiledata_event[xy_to_index(333, 30)] = 0
        data.tiledata_event[xy_to_index(333, 31)] = 0

        data.tiledata_event[xy_to_index(309, 16)] = 0
        data.tiledata_event[xy_to_index(309, 17)] = 0

    # warp destination
    if areaid == 8:
        # replace hospital bomb block to ribbon block for prevent softlock

        # box room
        data.tiledata_event[xy_to_index(485, 73)] = 6
        data.tiledata_event[xy_to_index(486, 73)] = 6

        # wall
        data.tiledata_event[xy_to_index(438, 64)] = 6
        data.tiledata_event[xy_to_index(438, 65)] = 6

    # sysint2
    if areaid == 9:
        # entrance
        data.tiledata_event[xy_to_index(197, 73)] = 0
        data.tiledata_event[xy_to_index(197, 74)] = 0

        # before the egg room
        data.tiledata_event[xy_to_index(150, 156)] = 0
        data.tiledata_event[xy_to_index(150, 157)] = 0

        data.tiledata_event[xy_to_index(144, 156)] = 0
        data.tiledata_event[xy_to_index(144, 157)] = 0

        data.tiledata_event[xy_to_index(108, 154)] = 0
        data.tiledata_event[xy_to_index(108, 155)] = 0

        data.tiledata_event[xy_to_index(112, 154)] = 0
        data.tiledata_event[xy_to_index(112, 155)] = 0

        data.tiledata_event[xy_to_index(88, 151)] = 0
        data.tiledata_event[xy_to_index(88, 152)] = 0

        data.tiledata_event[xy_to_index(137, 141)] = 0
        data.tiledata_event[xy_to_index(137, 142)] = 0

        data.tiledata_event[xy_to_index(54, 130)] = 0
        data.tiledata_event[xy_to_index(54, 131)] = 0

        # after the egg room
        data.tiledata_event[xy_to_index(130, 188)] = 0
        data.tiledata_event[xy_to_index(130, 189)] = 0

        data.tiledata_event[xy_to_index(158, 185)] = 0
        data.tiledata_event[xy_to_index(158, 186)] = 0

        data.tiledata_event[xy_to_index(167, 185)] = 0
        data.tiledata_event[xy_to_index(167, 186)] = 0

        data.tiledata_event[xy_to_index(177, 185)] = 0
        data.tiledata_event[xy_to_index(177, 186)] = 0

        data.tiledata_event[xy_to_index(190, 185)] = 0
        data.tiledata_event[xy_to_index(190, 186)] = 0

        data.tiledata_event[xy_to_index(200, 185)] = 0
        data.tiledata_event[xy_to_index(200, 186)] = 0

        data.tiledata_event[xy_to_index(209, 185)] = 0
        data.tiledata_event[xy_to_index(209, 186)] = 0

        data.tiledata_event[xy_to_index(215, 185)] = 0
        data.tiledata_event[xy_to_index(215, 186)] = 0

        data.tiledata_event[xy_to_index(208, 152)] = 0
        data.tiledata_event[xy_to_index(208, 153)] = 0

        data.tiledata_event[xy_to_index(203, 129)] = 0
        data.tiledata_event[xy_to_index(203, 130)] = 0
        # the last trampoline is left alone (296, 121-122)

def configure_shaft(mod, settings):
    events_list = []

    event_flag_set_list = []

    if settings.apply_fixes:
        # Turn on warp stones from the start
        event_flag_set_list += [(281,)]

    if settings.shuffle_start_location:
        # Disable starting forest warp from the start
        event_flag_set_list += [(297,), (298,)]

    if settings.shuffle_gift_items:
        # Disable event where miriam gives you speed boost and bunny strike.
        event_flag_set_list += [(374,), (378,)]
        # The P.Hairpin event is (453,), but I remove it from the maps in the diff instead of disabling it.

    if len(event_flag_set_list) > 0:
        events_list += [(525,)] + event_flag_set_list + [(524,)]

    if settings.open_mode:
        # Add ribbon
        events_list.append((558, 5008, 5001))

    # AP Change: Give player Strange Box, used to return to start.
    events_list.append((558, 5030, 5001))

    # Add attack ups
    if settings.hyper_attack_mode:
        for i in range(0,30):
            events_list.append((558, 5223-i, 5001))
        print_ln('Hyper attack mode applied')
    elif settings.super_attack_mode:
        for i in range(0,20):
            events_list.append((558, 5223-i, 5001))
        print_ln('Super attack mode applied')

    # Build shaft only if there is something to build.
    if len(events_list) > 0:
        for areaid, data in mod.stored_datas.items():
            build_start_game_shaft(areaid, data, events_list, settings)


def build_start_game_shaft(areaid, data, events_list, settings):
    # area 0 only.
    if areaid != 0: return

    bx, by, shaftx = 100, 0, 11
    if settings.shuffle_start_location:
        bx, by, shaftx = 60, 45, 10
    MAX_EVENTS = 39
    EVENT_COUNT = len(events_list)
    if EVENT_COUNT > MAX_EVENTS:
        fail('Too many events in start game shaft: %d/%d' % (EVENT_COUNT, MAX_EVENTS))

    # EV_MOVEDOWN event to move erina down to start position
    data.tiledata_event[xy_to_index(bx + shaftx, by + 43)] = 554

    # Place events in shaft
    for i, ev_tuple in enumerate(events_list):
        y = by + 43 - EVENT_COUNT + i
        for dx, ev in enumerate(ev_tuple):
            data.tiledata_event[xy_to_index(bx + shaftx + dx,y)] = ev

    # Remove old start event
    data.tiledata_event[xy_to_index(113,98)] = 0
    # Place new start event
    data.tiledata_event[xy_to_index(bx + shaftx, by + 42 - EVENT_COUNT)] = 34

    # Remove OoB light event
    data.tiledata_event[xy_to_index(68,90)] = 0

    # Add collision data
    data.tiledata_map[xy_to_index(bx + shaftx - 1, by + 44)] = 1
    data.tiledata_map[xy_to_index(bx + shaftx + 0, by + 44)] = 1
    data.tiledata_map[xy_to_index(bx + shaftx + 1, by + 44)] = 1
    for i in range(0,EVENT_COUNT+5):
        y = by + 43 - i
        data.tiledata_map[xy_to_index(bx + shaftx - 1, y)] = 1
        data.tiledata_map[xy_to_index(bx + shaftx + 1, y)] = 1
    data.tiledata_map[xy_to_index(bx + shaftx, by + 43 - EVENT_COUNT - 4)] = 1

    # Blanket with black graphical tiles
    for y in range(by, by + 45):
        for x in range(bx, bx + 20):
            data.tiledata_tiles2[xy_to_index(x,y)] = 33

    # Change room type and background
    mapy = round(by / 11.25 + 0.5)
    for y in range(mapy, mapy + 4):
        data.tiledata_roombg[to_tile_index(bx // 20, y)] = 56
        data.tiledata_roomtype[to_tile_index(bx // 20, y)] = 3


def apply_diff_patch_fixes(mod, diff_patch_files):
    def apply_diff(arrays, diffs):
        for layer_name, diff_list in diffs.items():
            array = arrays[layer_name]
            for diff in diff_list:
                for index, coords, value in diff:
                    array[index] = value

    area_arrays = {}
    for areaid, stored_data in mod.stored_datas.items():
        area_arrays[areaid] = {
            'roomtype': stored_data.tiledata_roomtype,
            'roomcolor': stored_data.tiledata_roomcolor,
            'roombg': stored_data.tiledata_roombg,
            'collision': stored_data.tiledata_map,
            'event': stored_data.tiledata_event,
            'tiles0': stored_data.tiledata_tiles0,
            'tiles1': stored_data.tiledata_tiles1,
            'tiles2': stored_data.tiledata_tiles2,
            'tiles3': stored_data.tiledata_tiles3,
            'tiles4': stored_data.tiledata_tiles4,
            'tiles5': stored_data.tiledata_tiles5,
            'tiles6': stored_data.tiledata_tiles6,
            'items': stored_data.tiledata_items
        }

    for diff_path_file in diff_patch_files:
        diff_data = diffgenerator.DiffData(diff_path_file)
        for areaid, diffs in diff_data.area_diffs.items():
            apply_diff(area_arrays[areaid], diffs)

def pre_modify_map_data(mod, settings, diff_patch_files, config):
    # apply beginner mod
    if settings.apply_beginner_mod:
        diff_patch_files.insert(0, os.path.join('existing_randomizer', 'maptemplates', 'beginner', 'mod_beginner.txt'))
        print_ln('Beginner mod applied')

    # apply rando fixes
    if settings.apply_fixes:
        for areaid, data in mod.stored_datas.items():
            apply_fixes_for_randomizer(areaid, data)
        # AP Change: Use os.path.join
        diff_patch_files += [
            os.path.join('existing_randomizer', 'maptemplates', 'event_warps', 'ew_cicini_to_ravine.txt'),
            os.path.join('existing_randomizer', 'maptemplates', 'event_warps', 'ew_forest_to_beach.txt'),
            os.path.join('existing_randomizer', 'maptemplates', 'event_warps', 'ew_town_to_riverbank.txt'),
            os.path.join('existing_randomizer', 'maptemplates', 'event_warps', 'ew_rumi_no_give_items.txt'),
            os.path.join('existing_randomizer', 'maptemplates', 'event_warps', 'ew_sandbag_no_boost.txt'),
            os.path.join('existing_randomizer', 'maptemplates', 'event_warps', 'ew_volcanic_bomb_bunny_open.txt'),
            os.path.join('existing_randomizer', 'maptemplates', 'event_warps', 'ew_fc2_no_void.txt'),
        ]
        print_ln('Map fixes applied')

    # Note: because musicrandomizer requires room color info, the music
    # must be shuffled before the room colors!

    # AP Change: Ensure music and background shuffle are consistent by seed
    rng = random.Random(settings.random_seed)
    if settings.shuffle_music:
        musicrandomizer.shuffle_music(mod.stored_datas, rng)

    if settings.shuffle_backgrounds:
        backgroundrandomizer.shuffle_backgrounds(mod.stored_datas, settings.no_laggy_backgrounds, settings.no_difficult_backgrounds, rng)

    # Add shaft if needed
    configure_shaft(mod, settings)

    # Apply map patches from list of patches. We apply this only after everything else has been applied.
    apply_diff_patch_fixes(mod, diff_patch_files)
    print_ln('Map patches applied')

    # Apply post game adjustments - remove tramplines and low% blocks
    if config.settings["POST_GAME_ALLOWED"]:
        for areaid, data in mod.stored_datas.items():
            apply_post_game_fixes(areaid, data)
        print_ln('Post Game map fixes applied')

    # Apply open mode after map patches because all it does is remove IDs 300 and 301.
    if settings.open_mode:
        for areaid, data in mod.stored_datas.items():
            apply_open_mode_fixes(areaid, data)
        print_ln('Open mode applied')


def apply_map_transition_shuffle(mod, data, settings, allocation):
    events_2d_dict = {}
    for areaid, tiledata in mod.stored_datas.items():
        tiledata_event = tiledata.tiledata_event
        events_2d_dict[areaid] = [tiledata_event[i:i+200] for i in range(0,len(tiledata_event),200)]

    def set_target_in_map(transition, area_target, entry_target):
        events_2d = events_2d_dict[transition.area_current]
        tiledata_event = mod.stored_datas[transition.area_current].tiledata_event
        x1,y1,w,h = transition.rect
        events_cropped = [x for row in events_2d[x1:x1+w] for x in row[y1:y1+h]]

        original_map_event = transition.area_target + 161
        original_entry_event = transition.entry_target + 200
        new_map_event = area_target + 161
        new_entry_event = entry_target + 200

        for i in (i for i,ev in enumerate(events_cropped) if ev == original_map_event):
            tiledata_event[xy_to_index(x1+i//h, y1+i%h)] = new_map_event

        for i in (i for i,ev in enumerate(events_cropped) if ev == original_entry_event):
            tiledata_event[xy_to_index(x1+i//h, y1+i%h)] = new_entry_event

    for rtr, ltr in zip(data.walking_right_transitions, allocation.walking_left_transitions):
        set_target_in_map(rtr, ltr.area_current, ltr.entry_current)
        set_target_in_map(ltr, rtr.area_current, rtr.entry_current)


def apply_start_location_shuffle(mod, settings, allocation):
    """
    AP Changes:
        Removed unnecessary for loop over area list.
        Changed location of start location teleporter.
        Added event update for number of eggs to reach trophy.
    """
    if not settings.shuffle_start_location: return
    # Add start warp room and remove FC2 warp stone
    # AP Change: Use os.path.join
    apply_diff_patch_fixes(mod, [
        os.path.join('existing_randomizer', 'maptemplates', 'event_warps', 'ew_start_room.txt'),
        os.path.join('existing_randomizer', 'maptemplates', 'event_warps', 'ew_fc2_to_start.txt'),
    ])

    start_area = allocation.start_location.area

    # Add warp exit point to original start position
    area0_data = mod.stored_datas[0]
    area0_data.tiledata_event[xy_to_index(112, 91)] = 218
    area0_data.tiledata_event[xy_to_index(112, 92)] = 240

    # Update teleporter in start warp room to point to area of start position
    cross_map_event_id = 242 + start_area
    for y in range(130, 133):
        for x in range(82, 88):
            if area0_data.tiledata_event[xy_to_index(x, y)] == 243:
                area0_data.tiledata_event[xy_to_index(x, y)] = cross_map_event_id

    # Update required egg count for trophy
    for y in range(129, 132):
        for x in range(54, 58):
            if area0_data.tiledata_event[xy_to_index(x, y)] == 5005:
                area0_data.tiledata_event[xy_to_index(x, y)] = 5000 + settings.num_hard_to_reach

    # Add warp exit point to the random start location
    start_area_data = mod.stored_datas[start_area]
    x, y = allocation.start_location.position
    start_area_data.tiledata_event[xy_to_index(x, y)] = 220
    start_area_data.tiledata_event[xy_to_index(x, y + 1)] = 240

def insert_items_into_map(mod, data, settings, allocation):
    """
    AP Changes:
        Increment duplicate item ids based on the same name
    """
    cur_stat_boost_ids = {
        "ATTACK_UP": 160,
        "HP_UP": 96,
        "PACK_UP": 352,
        "MP_UP": 224,
        "REGEN_UP": 288
    }

    name_to_id = dict((item.name, item.itemid) for item in data.items)
    name_to_id.update(data.additional_items)

    mod.clear_items()
    for original_item in data.items:
        item = original_item.copy()
        if item.name not in allocation.item_at_item_location:
            continue
        item_at_location = allocation.item_at_item_location[item.name]
        # AP Change: Place player's own "Nothing" as an AP item
        # to behave better with AP's hint point system.
        if item_at_location != None:
            if item_at_location in cur_stat_boost_ids:
                item.itemid = cur_stat_boost_ids[item_at_location]
                cur_stat_boost_ids[item_at_location] += 1
            elif item_at_location == "ANOTHER_PLAYERS_ITEM" or item_at_location == "NOTHING":
                item.itemid = 43
            elif item_at_location == "EASTER_EGG":
                item.itemid = -250
            else:
                item.itemid = name_to_id[item_at_location]
            mod.add_item(item)


def get_default_areaids():
    return list(range(10))

def reset_maps(source_dir, output_dir):
    if not os.path.isdir(output_dir):
        fail('Output directory %s does not exist' % output_dir)
    mapfileio.grab_original_maps(source_dir, output_dir)
    analysis_file = '%s/analysis.txt' % output_dir
    if os.path.isfile(analysis_file):
        os.remove(analysis_file)
    print_ln('Original maps copied to %s.' % output_dir)

def display_hash(settings):
    areaids = get_default_areaids()
    hash_digest = hash_map_files(areaids, settings.output_dir)
    print_ln('Hash: %s' % hash_digest)


def generate_analysis_file(data, allocation, analyzer, difficulty_analysis, settings, seed):
    analysis_lines = []
    def print_to_analysis(line=''):
        print_ln(line)
        analysis_lines.append(str(line))

    def print_to_analysis_only(line=''):
        analysis_lines.append(str(line))

    def print_setting_bool(setting_name, setting_bool):
        print_to_analysis_only('%s: %s' % (setting_name, 'On' if setting_bool else 'Off'))

    def print_setting_int(setting_name, setting_int):
        print_to_analysis_only('%s: %d' % (setting_name, setting_int))

    low = int(0.5 * settings.constraint_changes)
    high = int(1.5 * settings.constraint_changes + 2)
    if settings.constraint_changes <= 0:
        high = 0
    if settings.min_constraint_changes >= 0:
        low = int(settings.min_constraint_changes)
    if settings.max_constraint_changes >= 0:
        high = int(settings.max_constraint_changes + 2)
    changes = int((high + low) / 2 - 1)

    print_to_analysis_only('--- Randomizer Flags ---')
    print_setting_bool('Shuffle Gift Items', settings.shuffle_gift_items)
    print_setting_bool('Shuffle Map Transitions', settings.shuffle_map_transitions)
    print_setting_int('Approximate Number of Constraint Changes', changes)
    print_setting_bool('Shuffle Music', settings.shuffle_music)
    print_setting_bool('Shuffle Backgrounds', settings.shuffle_backgrounds)
    print_setting_bool('No Laggy Backgrounds', settings.no_laggy_backgrounds)
    print_setting_bool('No Difficult Backgrounds', settings.no_difficult_backgrounds)

    print_setting_bool('Super Attack Mode', settings.super_attack_mode)
    print_setting_bool('Hyper Attack Mode', settings.hyper_attack_mode)
    print_setting_bool('Open Mode', settings.open_mode)
    print_setting_bool('Apply Map Fixes', settings.apply_fixes)

    print_setting_int('Number of Hard-to-Reach Items', settings.num_hard_to_reach)
    print_setting_bool('Egg Goals', settings.egg_goals)
    print_setting_int('Number of Extra Eggs', settings.extra_eggs)
    print_to_analysis_only()

    config_data = data.config_data
    print_to_analysis_only('--- Generation Settings ---')
    print_to_analysis_only('Knowledge: %s' % config_data.knowledge)
    print_to_analysis_only('Difficulty: %s' % config_data.difficulty)

    print_to_analysis_only('Settings:')
    for key, value in config_data.settings.items():
        print_to_analysis_only('    %s: %s' % (key, 'true' if value else 'false'))
    print_to_analysis_only()

    print_to_analysis_only('--- Generation Results ---')
    if settings.egg_goals:
        print_to_analysis('Number of eggs: %d' % allocation.count_eggs())
    else:
        print_to_analysis('Hard to Reach Items:')
        for item_name in analyzer.hard_to_reach_items:
            print_to_analysis('    %s' % item_name)


    if not settings.hide_difficulty:
        print_to_analysis('Difficulty: %.2f' % difficulty_analysis.difficulty_score)
        print_to_analysis('Sequence Break Potential: %.2f' % difficulty_analysis.breakability_score)
        print_to_analysis('Seed: %x' % seed)
        print_to_analysis_only()


    if not settings.no_write:
        f = open('%s/%s' % (settings.output_dir, 'analysis.txt'), 'w+')
        f.write('\n'.join(analysis_lines))
        f.close()

    if settings.debug_visualize:
        levels = analyzer.levels
        f = open('%s/spoiler/%s' % (settings.output_dir, 'chain.txt'), 'w+')

        item_location_at_item = {}
        for k, v in allocation.item_at_item_location.items():
            if v != None:
                item_location_at_item[v] = k

        f.write("start location: %s\n\n" % allocation.start_location.location)
        f.write("picked templates: %s\n\t" % len(allocation.picked_templates))
        f.write("\n\t".join(sorted([t.name for t in allocation.picked_templates])))
        f.write("\n\n")

        lv = 0
        while len(levels) > lv:
            f.write("--- chain %d ---\n" % (lv/2))
            if len(levels[lv]) > 0:
                f.write("\npseudo items:\n\t")
                f.write("\n\t".join(levels[lv]))

            level = levels[lv+1]

            locs = set(name for name in level if name in data.locations_set)
            objs = sorted(set(level) - locs)
            eggs = list(name for name in objs if is_egg(name))
            items = list(name for name in objs if not is_potion(name) and not is_egg(name))
            potions = list(name for name in objs if is_potion(name))

            sorted_items = eggs + items + potions
            if len(sorted_items) > 0:
                f.write("\nitems:\t")
                for v in sorted_items:
                    k = "[Additional items]"
                    if v in item_location_at_item:
                        k = item_location_at_item[v]
                    f.write("\n\t%s @ %s" % (v, k))
            if len(locs) > 0:
                f.write("\nlocations:\n\t")
                f.write("\n\t".join(sorted(locs)))
            f.write("\n\n")

            lv += 2

        f.close()

def run_randomizer(seed, settings):
    randomizer_data = RandomizerData(settings)
    generator = Generator(randomizer_data, settings)
    allocation, analyzer, difficulty_analysis, seed = generator.generate_seed(seed)
    #print_ln('done')

    generate_analysis_file(randomizer_data, allocation, analyzer, difficulty_analysis, settings, seed)

    if settings.no_write:
        print_ln('No maps generated as no-write flag is on.')
        return

    areaids = get_default_areaids()
    if not mapfileio.exists_map_files(areaids, settings.source_dir):
        fail('Maps not found in the directory %s! Place the original Rabi-Ribi maps '
             'in this directory for the randomizer to work.' % settings.source_dir)

    mapfileio.grab_original_maps(settings.source_dir, settings.output_dir)
    print_ln('Maps copied...')
    mod = mapfileio.ItemModifier(areaids, source_dir=settings.source_dir)
    pre_modify_map_data(mod, settings, allocation.map_modifications, randomizer_data.config_data)
    apply_item_specific_fixes(mod, allocation)
    apply_map_transition_shuffle(mod, randomizer_data, settings, allocation)
    apply_start_location_shuffle(mod, settings, allocation)
    insert_items_into_map(mod, randomizer_data, settings, allocation)

    mod.save(settings.output_dir)
    print_ln('Maps saved successfully to %s.' % settings.output_dir)

    display_hash(settings)


# if __name__ == '__main__':
#     args = parse_args()

#     if args.version:
#         print_ln('Rabi-Ribi Randomizer - %s' % versioncheck.VERSION_STRING)
#     elif args.check_for_updates:
#         versioncheck.check_for_updates()
#     elif args.check_branch:
#         versioncheck.check_branch()
#     elif args.hash:
#         display_hash(args)
#     elif args.reset:
#         reset_maps(args.source_dir, args.output_dir)
#     else:
#         if args.seed == None: seed = None
#         else: seed = string_to_integer_seed(args)
#         run_randomizer(seed, args)

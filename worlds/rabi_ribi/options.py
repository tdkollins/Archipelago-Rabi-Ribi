"""This module represents option defintions for Rabi-Ribi"""
from dataclasses import dataclass

from Options import PerGameCommonOptions, Choice, Range, Toggle, DeathLink

class OpenMode(Toggle):
    """Gain access to Chapter 1 areas without needing to complete the prologue"""
    display_name = "Open Mode"
    default = True

class RandomizeHammer(Toggle):
    """If set to false, the hammer is at the default location"""
    display_name = "Randomize Hammer"

class RandomizeGiftItems(Toggle):
    """If set to false, items given by NPCs (Speed Boost, Bunny Strike, P Hairpin) are at their default locations"""
    display_name = "Randomize Gift Items"

class CarrotShooterInLogic(Toggle):
    """
    If set to false, carrot shooter will not be required to bomb locations.
    These locations will be locked behind carrot bomb instead.
    """
    display_name = "Carrot Shooter In Logic"

class EncourageEggsInLateSpheres(Toggle):
    """
    If set to true, the randomizer logic will attempt to place eggs in later spheres
    resulting in harder to get to eggs.
    """
    display_name = "Encourage Eggs In Late Spheres"

class Knowledge(Choice):
    """
    Knowledge can be BASIC, INTERMEDIATE, ADVANCED, or OBSCURE.

    There are many tricks in the game that requires advanced knowledge of how the game works to perform.
    Knowledge levels (mostly) align with the tricks explained on each section of the Platforming Tricks Tutorial custom map.
    Obscure contains tricks that require incredibly specific game knowledge and may be scarcely documented, if at all.
    """
    display_name = "Knowledge"
    option_basic = 0
    option_intermediate = 1
    option_advanced = 2
    option_obscure = 3
    default = option_basic

class TrickDifficulty(Choice):
    """
    Difficulty can be NORMAL, HARD, V_HARD, EXTREME, or STUPID.

    Some tricks in Rabi-Ribi can be very difficult to execute. This flag determines the minimum execution ability required to complete the seed.

    Normal is recommended for most players. There are many tight jumps which are still labeled as NORMAL.
    Hard involves some tricks that are tight, and can be difficult to execute for newer players.
    V_Hard involves some tricks that are very tight, and can be difficult to execute even for experienced players.
    Extreme involves tricks that can be quite unreasonable to be expected to execute.
    Stupid refers to tricks that no one wants to do, ever. This often refers to tricks that have only been performed successfully once, just to prove that it is possible.
    """
    display_name = "Trick Difficulty"
    option_normal = 0
    option_hard = 1
    option_v_hard = 2
    option_extreme = 3
    option_stupid = 4
    default = option_normal

class BlockClipsRequired(Toggle):
    """
    Block clips are performed by quick-dropping onto the top of a one-tile block to obtain the item inside the block.
    Turning off this flag removes the need for block clips.
    """
    display_name = "Block Clips Required"

class SemiSolidClipsRequired(Toggle):
    """
    Semisolid Clips refers to clipping through semisolid
    (one-way) platforms via a specific glitch. If this flag is turned on,
    reaching some of the items may require semisolid clips to be performed.
    If turned off, all the required items can be obtained without the need
    for semisolid clips.
    """
    display_name = "Semi Solid Clips Required"

class ZipsRequired(Toggle):
    """
    Zips are glitches that allow you to clip through terrain.
    The main types of zips are slide zips and hammer roll zips.
    If this flag is turned on, reaching some of the items may require
    zips to be performed. If turned off, all the required items can be
    obtained without the need for zips.
    """
    display_name = "Zips Required"

class BunstrikeZipsRequired(Toggle):
    """
    A bunstrike zip is an obscure zip method performed by using Bunny Strike.
    If this flag is turned on, reaching some of the items may require
    bunstrike zips to be performed. If turned off, all the required items
    can be obtained without the need for bunstrike zips.
    """
    display_name = "Bunstrike Zips Required"

class BoringTricksRequired(Toggle):
    """
    If this flag is true, some of the items may require performing tricks
    considered too boring or tedious to normally be included in logic.
    Note that most of these tricks are still considered to be at least
    Advanced knowledge and Very Hard difficulty at minimum.
    """
    display_name = "Boring Tricks Required"

class DarknessWithoutLightOrb(Toggle):
    """
    If this flag is true, the game might expect you to go into dark areas,
    even if you don’t have the Light Orb.
    """
    display_name = "Darkness Without Light Orb"

class UnderwaterWithoutWaterOrb(Toggle):
    """
    If this flag is true, the game might expect you to go into underwater areas,
    even if you don’t have the Water Orb.
    """
    display_name = "Underwater Without Water Orb"

class IncludePlurkwood(Toggle):
    """
    If this flag is true, the game might expect you to go into Plurkwood.
    """
    display_name = "IncludePlurkwood"

class IncludeWarpDestination(Toggle):
    """
    If this flag is true, locations in the warp destination area are included in the pool.
    Note that some of these locations may require beating the game to reach again if missed.
    """
    display_name = "Include Warp Destination"

class IncludePostGame(Toggle):
    """
    If this flag is true, locations only reachable in the post game are included in the pool.
    """
    display_name = "Include Post Game"

class IncludePostIrisu(Toggle):
    """
    If this flag is true, locations after beating Irisu are included in the pool.
    """
    display_name = "Include Post Irisu"

class IncludeHalloween(Toggle):
    """
    If this flag is true, the Halloween DLC locations are included in the pool.
    Requires the "Cinini's Halloween!" DLC.
    """
    display_name = "Include Halloween DLC"

class EventWarpsInLogic(Toggle):
    """
    If this flag is true, events that warp the player to another location are considered in logic.
    While some of these events can only be reached once normally, the randomizer adds doors that
    allow these events to be accessed multiple times.
    """
    display_name = "Event Warps in Logic"

class AttackMode(Choice):
    """
    Normal attack mode starts you with 0 attack ups.
    Super attack mode starts you with 20 attack ups.
    Hyper attack mode starts you with 30 attack ups.

    This gives you a lot more damage, which is especially useful because you often don't get
    the hammer early in randomizer games. (Ribbon does about 20 damage per shot in super attack mode)
    """
    display_name = "Attack Mode"
    option_normal = 0
    option_super = 1
    option_hyper = 2
    default = option_normal

class EnableConstraintChanges(Toggle):
    """
    If this flag is true, the randomizer will choose a number of predefined map
    edits to restrict access to areas.
    """
    display_name = "Enable Map Constraints"

class NumberOfConstraintChanges(Range):
    """
    Sets the total number of map constraint changes to be added.
    """
    display_name = "Number of Map Constraint Changes"
    range_start = 0
    range_end = 70

class ShuffleMapTransitions(Toggle):
    """
    If this flag is true, the randomizer will shuffle the entrances between maps.
    """
    display_name = "Shuffle Map Transitions"

class ShuffleMusic(Toggle):
    """
    If this flag is true, the randomizer will shuffle the music tracks played in each area.
    """
    display_name = "Shuffle Music"

class ShuffleBackgrounds(Toggle):
    """
    If this flag is true, the randomizer will shuffle the room backgrounds in each area.
    Note that some backgrounds that introduce lag or make tricks difficult to perform are disabled.
    """
    display_name = "Shuffle Backgrounds"

class ShuffleStartLocation(Toggle):
    """
    If this flag is true, the randomizer will start the player at one of several locations
    around Rabi Rabi Island.
    """
    display_name = "Shuffle Start Location"

@dataclass
class RabiRibiOptions(PerGameCommonOptions):
    """Rabi Ribi Options Definition"""
    open_mode: OpenMode
    knowledge: Knowledge
    trick_difficulty: TrickDifficulty
    block_clips_required: BlockClipsRequired
    semi_solid_clips_required: SemiSolidClipsRequired
    zips_required: ZipsRequired
    bunstrike_zips_required: BunstrikeZipsRequired
    boring_tricks_required: BoringTricksRequired
    darkness_without_light_orb: DarknessWithoutLightOrb
    underwater_without_water_orb: UnderwaterWithoutWaterOrb
    carrot_shooter_in_logic: CarrotShooterInLogic
    event_warps_in_logic: EventWarpsInLogic

    attack_mode: AttackMode
    encourage_eggs_in_late_spheres: EncourageEggsInLateSpheres

    randomize_hammer: RandomizeHammer
    randomize_gift_items: RandomizeGiftItems

    include_plurkwood: IncludePlurkwood
    include_warp_destination: IncludeWarpDestination
    include_post_game: IncludePostGame
    include_post_irisu: IncludePostIrisu
    include_halloween: IncludeHalloween

    number_of_constraint_changes: NumberOfConstraintChanges
    shuffle_map_transitions: ShuffleMapTransitions
    shuffle_start_location: ShuffleStartLocation
    shuffle_music: ShuffleMusic
    shuffle_backgrounds: ShuffleBackgrounds
    death_link: DeathLink

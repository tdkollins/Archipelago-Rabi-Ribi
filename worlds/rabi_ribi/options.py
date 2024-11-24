"""This module represents option defintions for Rabi-Ribi"""
from dataclasses import dataclass

from Options import PerGameCommonOptions, Choice, Range, Toggle

class OpenMode(Toggle):
    """Gain access to chapter 1 areas without needing to complete the prologue"""
    display_name = "Open Mode"

class RandomizeHammer(Toggle):
    """If set to false, the hammer is at the default location"""
    display_name = "Randomize Hammer"

class RandomizeGiftItems(Toggle):
    """If set to false, items given by NPCs (Speed Boost, Hammer Strike, P Hairpin) are at their default locations"""
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
    Knowledge can be BASIC, INTERMEDIATE or ADVANCED.

    There are many tricks in the game that requires advanced knowledge of how the game works to perform.

    Basic is recommended for anyone not familiar with speedrunning tricks used in Rabi-Ribi.
    Intermediate is recommended for players who are already very familiar with the advanced speedrunning tricks used in Rabi-Ribi.
    Advanced tricks require extremely specific knowledge, and is not recommended unless you are always keeping up to date with the very specific tricks used to get into certain areas in the game.
    """
    display_name = "Knowledge"
    option_basic = 0
    option_intermediate = 1
    option_advanced = 2
    default = option_basic

class TrickDifficulty(Choice):
    """
    Difficulty can be NORMAL, HARD, V_HARD or STUPID.

    Some tricks in Rabi-Ribi can be very difficult to execute. This flag determines the minimum execution ability required to complete the seed.

    Normal is recommended for most players. There are many tight jumps which are still labeled as NORMAL.
    Hard involves some tricks that are very tight, and can be difficult to execute even for experienced players. However, these tricks are still reasonable.
    V_Hard involves tricks that can be quite unreasonable to be expected to execute (i.e. borderline stupid), but some people still do them anyway.
    Stupid refers to tricks that no one wants to do, ever. This often refers to tricks that have only been performed successfully once, just to prove that it is possible.
    """
    display_name = "Trick Difficulty"
    option_normal = 0
    option_hard = 1
    option_v_hard = 2
    option_stupid = 3
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

class PlurkwoodReachable(Toggle):
    """
    If this flag is true, the game might expect you to go into Plurkwood.
    """
    display_name = "Plurkwood Reachable"

class AttackMode(Choice):
    """
    Normal attack mode starts you with 0 attack ups.
    Super attack mode starts you with 20 attack ups.
    Hyper attack mode starts you with 30 attack ups.

    This gives you a lot more damage, which is especially useful because you often don’t get
    the hammer early in randomizer games. (Ribbon does about 20 damage per shot in super attack mode)
    """
    display_name = "Attack Mode"
    option_normal = 0
    option_super = 1
    option_hyper = 2
    default = option_normal


@dataclass
class RabiRibiOptions(PerGameCommonOptions):
    """Rabi Ribi Options Definition"""
    open_mode: OpenMode
    randomize_hammer: RandomizeHammer
    randomize_gift_items: RandomizeGiftItems
    knowledge: Knowledge
    trick_difficulty: TrickDifficulty
    block_clips_required: BlockClipsRequired
    semi_solid_clips_required: SemiSolidClipsRequired
    zips_required: ZipsRequired
    darkness_without_light_orb: DarknessWithoutLightOrb
    underwater_without_water_orb: UnderwaterWithoutWaterOrb
    attack_mode: AttackMode
    encourage_eggs_in_late_spheres: EncourageEggsInLateSpheres
    carrot_shooter_in_logic: CarrotShooterInLogic
    plurkwood_reachable: PlurkwoodReachable

"""
This module defines all of the logic macros that are to be used
when parsing access rules from the existing randomizer.
"""
from rule_builder import rules
from .bases import RabiRibiWorldBase
from .custom_rules import (
    HasEnoughAmuletFoodRule,
    Macro,
    KnowledgeRule,
    MagicTypesRule,
    OutOfLogicOptionRule,
    TrickDifficultyRule,
    TownMemberCountRule,
    TownMemberCountIrisuRule
)
from .data import data
from .names import ItemName, LocationName
from .options import *

# Knowledge and Trick Difficulty
intermediate = Macro(
    KnowledgeRule(Knowledge.option_intermediate),
    "ITM",
    "Assumes the player has knowledge of intermediate-level tricks"
)

advanced = Macro(
    KnowledgeRule(Knowledge.option_advanced),
    "ADV",
    "Assumes the player has knowledge of advanced-level tricks"
)

obscure = Macro(
    KnowledgeRule(Knowledge.option_obscure),
    "OBS",
    "Assumes the player has knowledge of obscure tricks"
)

hard = Macro(
    TrickDifficultyRule(TrickDifficulty.option_hard),
    "HARD",
    "Assumes the player can execute tricks rated hard"
)

vhard = Macro(
    TrickDifficultyRule(TrickDifficulty.option_v_hard),
    "VHARD",
    "Assumes the player can execute tricks rated very hard"
)

extreme = Macro(
    TrickDifficultyRule(TrickDifficulty.option_extreme),
    "EXT",
    "Assumes the player can execute tricks rated extreme"
)

stupid = Macro(
    TrickDifficultyRule(TrickDifficulty.option_stupid),
    "STUPID",
    "Assumes the player can execute tricks rated stupid")

itm_hard = Macro(
    intermediate & hard,
    "ITM_HARD",
    "Assumes the player has knowledge of intermediate-level tricks and can execute tricks rated hard"
)

itm_vhard = Macro(
    intermediate & vhard,
    "ITM_VHARD",
    "Assumes the player has knowledge of intermediate-level tricks and can execute tricks rated very hard"
)

adv_hard = Macro(
    advanced & hard,
    "ADV_HARD",
    "Assumes the player has knowledge of advanced-level tricks and can execute tricks rated hard"
)

adv_vhard = Macro(
    advanced & vhard,
    "ADV_VHARD",
    "Assumes the player has knowledge of advanced-level tricks and can execute tricks rated very hard"
)

adv_ext = Macro(
    advanced & extreme,
    "ADV_EXT",
    "Assumes the player has knowledge of advanced-level tricks and can execute tricks rated extreme"
)

adv_stupid = Macro(
    advanced & stupid,
    "ADV_STUPID",
    "Assumes the player has knowledge of advanced-level tricks and can execute tricks rated stupid"
)

obs_hard = Macro(
    obscure & hard,
    "OBS_HARD",
    "Assumes the player has knowledge of obscure tricks and can execute tricks rated hard"
)

obs_vhard = Macro(
    obscure & vhard,
    "OBS_VHARD",
    "Assumes the player has knowledge of obscure tricks and can execute tricks rated very hard"
)

obs_ext = Macro(
    obscure & extreme,
    "OBS_EXT",
    "Assumes the player has knowledge of obscure tricks and can execute tricks rated extreme"
)

obs_stupid = Macro(
    obscure & stupid,
    "OBS_STUPID",
    "Assumes the player has knowledge of obscure tricks and can execute tricks rated stupid"
)

# Options
can_zip = OutOfLogicOptionRule("Zip", ZipsRequired, True)
can_semi_solid_clip = OutOfLogicOptionRule("Semisolid Clip", SemiSolidClipsRequired, True)
can_block_clip = OutOfLogicOptionRule("Block Clip", BlockClipsRequired, True)
can_do_boring_tricks = OutOfLogicOptionRule("Boring", BoringTricksRequired, True)
can_bunstrike_zip = OutOfLogicOptionRule("Bunstrike Zip", BunstrikeZipsRequired, True)
can_use_carrot_shooter = OutOfLogicOptionRule("Carrot Shooter", CarrotShooterInLogic, True)
can_use_event_warps = OutOfLogicOptionRule("Event Warp", EventWarpsInLogic, True)
can_enter_plurkwood = OutOfLogicOptionRule("Plurkwood", IncludePlurkwood, True)
can_enter_warp_destination = OutOfLogicOptionRule("Warp Destination", IncludeWarpDestination, True)
can_enter_post_game = OutOfLogicOptionRule("Post-Game", IncludePostGame, True)
can_enter_post_irisu = OutOfLogicOptionRule("Post-Irisu", IncludePostIrisu, True)
can_enter_halloween = OutOfLogicOptionRule("Halloween", IncludeHalloween, True)
darkness_without_light_orb = OutOfLogicOptionRule("Darkness", DarknessWithoutLightOrb, True)
underwater_without_water_orb = OutOfLogicOptionRule("Underwater", UnderwaterWithoutWaterOrb, True)

# Events
# Contains in-game events
shop_reachable = rules.Has("Shop Reachable")
boost_unlocked = rules.Has("Boost Unlocked")

ashuri_2 = rules.Has(ItemName.ashuri_2)
cocoa_1 = rules.Has(ItemName.cocoa_1)
kotri_1 = rules.Has(ItemName.kotri_1)
kotri_2 = rules.Has(ItemName.kotri_2)
seana_1 = rules.Has(ItemName.seana_1)

chapter_1 = rules.Has("Chapter 1")
chapter_2 = rules.Has("Chapter 2")
chapter_3 = rules.Has("Chapter 3")
chapter_4 = rules.Has("Chapter 4")
chapter_5 = rules.Has("Chapter 5")
chapter_6 = rules.Has("Chapter 6")
chapter_7 = rules.Has("Chapter 7")

boss_keke_bunny = Macro(
    rules.CanReachRegion(data.get_region_ap_name(LocationName.plurkwood_main)),
    "Fought Keke Bunny",
    "Player can fight Keke Bunny in Plurkwood"
)

boss_ribbon = Macro(
    rules.CanReachRegion(data.get_region_ap_name(LocationName.spectral_warp)),
    "Fought Ribbon",
    "Player can fight Ribbon in Spectral Cave"
)

# Pseudo Items
# Contains items and upgrades related to shop purchases and story events
wall_jump_lv2 = Macro(
    rules.Has(ItemName.wall_jump) & shop_reachable,
    "Wall Jump Lv2",
    "Player can upgrade Wall Jump to Level 2"
)

hammer_roll_lv3_upgrade = Macro(
    rules.Has(ItemName.hammer_roll) & shop_reachable & chapter_3,
    "Hammer Roll Lv3 Upgrade",
    "Player can upgrade Hammer Roll to Level 3"
)

air_dash_lv3_upgrade = Macro(
    rules.Has(ItemName.air_dash) & shop_reachable,
    "Air Dash Lv3 Upgrade",
    "Player can upgrade Air Dash to Level 3"
)

speed_boost_lv3 = Macro(
    rules.Has(ItemName.speed_boost) & shop_reachable,
    "Speed Boost Lv3",
    "Player can upgrade Speed Boost to Level 3"
)

bunny_amulet = Macro(
    rules.Has(ItemName.bunny_amulet) | chapter_2,
    "Bunny Amulet",
    "Player has Bunny Amulet"
)

bunny_amulet_lv2 = Macro(
    rules.Has(ItemName.bunny_amulet) & (shop_reachable | chapter_3 | chapter_7),
    "Bunny Amulet Lv2",
    "Player can upgrade Bunny Amulet to Level 2"
)

bunny_amulet_lv3 = Macro(
    rules.Has(ItemName.bunny_amulet) & (shop_reachable | chapter_4 | chapter_7),
    "Bunny Amulet Lv3",
    "Player can upgrade Bunny Amulet to Level 3"
)

bunny_amulet_lv4 = Macro(
    rules.Has(ItemName.bunny_amulet) & chapter_7,
    "Bunny Amulet Lv4",
    "Player can upgrade Bunny Amulet to Level 4"
)

piko_hammer_leveled = Macro(
    rules.Has(ItemName.piko_hammer),
    "Piko Hammer Leveled",
    "Player has leveled up the Piko Hammer through combat"
)

carrot_bomb_entry = Macro(
    rules.Has(ItemName.carrot_bomb),
    "Carrot Bomb Entry",
    "Player can enter a region using Carrot Bombs"
)

carrot_shooter_entry = Macro(
    rules.Has(ItemName.carrot_shooter),
    "Carrot Shooter Entry",
    "Player can enter a region using a Carrot Shooter charge shot"
)

charge_carrot_shooter_entry = Macro(
    rules.HasAll(ItemName.carrot_shooter, ItemName.charge_ring),
    "Charge Ring Carrot Shooter Entry",
    "Player can enter a region using a Carrot Shooter charge shot with Charge Ring"
)

speedy = Macro(
    intermediate & rules.Has(ItemName.cicini_recruit) & chapter_1 & TownMemberCountRule(3),
    "Speedy",
    "Player can obtain the Speedy buff from Cicini"
)

item_menu = Macro(
    chapter_1 | (advanced & MagicTypesRule(3)),
    "Item Menu",
    "Player can open the quick item menu"
)

consumable_use = Macro(
    item_menu & (rules.HasGroupUnique("Consumables") | shop_reachable),
    "Consumable Use",
    "Player can use a consumable item"
)

many_amulet_food = Macro(
    item_menu & shop_reachable & bunny_amulet,
    "Many Amulet and Food",
    "Player can use a large amount of Bunny Amulet charges and consumables by purchasing them"
)

boost = Macro(
    boost_unlocked | (rules.Has(ItemName.rumi_donut) & item_menu),
    "Boost",
    "Player can use boost attack"
)

boost_many = Macro(
    item_menu & shop_reachable,
    "Boost Many",
    "Player can use several boost attacks in a row"
)

boost_boring = Macro(
    (boost_unlocked & can_do_boring_tricks) | (rules.Has(ItemName.rumi_donut) & item_menu),
    "Boost Boring",
    "Player can use several boost attacks by farming boost charge or using a Rumi Donut"
)

# Items
# Contains logic to use an item
bunny_strike = Macro(
    rules.HasAll(ItemName.piko_hammer, ItemName.sliding_powder, ItemName.bunny_strike),
    "Bunny Strike",
    "Player can use Bunny Strike"
)

bunny_whirl = Macro(
    rules.HasAll(ItemName.piko_hammer, ItemName.bunny_whirl),
    "Bunny Whirl",
    "Player can use Bunny Whirl"
)

air_dash = Macro(
    rules.HasAll(ItemName.piko_hammer, ItemName.air_dash),
    "Air Dash",
    "Player can use Air Dash"
)

air_dash_lv3 = Macro(
    rules.Has(ItemName.piko_hammer) & air_dash_lv3_upgrade,
    "Air Dash Lv3",
    "Player can use Air Dash Lv3"
)

hammer_roll = Macro(
    rules.HasAll(ItemName.piko_hammer, ItemName.bunny_whirl, ItemName.hammer_roll),
    "Hammer Roll",
    "Player can use Hammer Roll"
)

hammer_roll_lv3 = Macro(
    rules.HasAll(ItemName.piko_hammer, ItemName.bunny_whirl) & hammer_roll_lv3_upgrade,
    "Hammer Roll Lv3",
    "Player can use Hammer Roll Lv3"
)

darkness = Macro(
    rules.Has(ItemName.light_orb) | darkness_without_light_orb,
    "Navigate Darkness",
    "Player can navigate dark rooms"
)

underwater = Macro(
    rules.Has(ItemName.water_orb) | underwater_without_water_orb,
    "Navigate Underwater",
    "Player can navigate underwater"
)

carrot_shooter = Macro(
    rules.Has(ItemName.carrot_shooter) & can_use_carrot_shooter,
    "Carrot Shooter",
    "Player can use Carrot Shooter"
)

explosives = Macro(
    rules.Has(ItemName.carrot_bomb) | (carrot_shooter & boost),
    "Explosives",
    "Player can destory bombable tiles using explosives"
)

explosives_enemy = Macro(
    rules.Has(ItemName.carrot_bomb) | carrot_shooter,
    "Explosives With Enemy",
    "Player can destory bombable tiles using explosives, using an enemy if the explosives are from the Carrot Shooter's charge shot"
)

speed1 = Macro(
    rules.Has(ItemName.speed_boost) | speedy,
    "Speed Lv1",
    "Player has a way to get a level 1 speed boost"
)

speed2 = Macro(
    speed_boost_lv3 | speedy,
    "Speed Lv2",
    "Player has a way to get a level 2 speed boost"
)

speed3 = Macro(
    speed_boost_lv3 | (rules.Has(ItemName.speed_boost) & speedy),
    "Speed Lv3",
    "Player has a way to get a level 3 speed boost"
)

speed5 = Macro(
    speed_boost_lv3 & speedy,
    "Speed Lv5",
    "Player has a way to get a level 5 speed boost"
)

# Tricks
# Contains logic to perform a trick
hammer_roll_zip = Macro(
    can_zip & hammer_roll_lv3,
    "Hammer Roll Zip",
    "Player can perform a zip with Hammer Roll"
)

slide_zip = Macro(
    can_zip & rules.Has(ItemName.sliding_powder),
    "Slide Zip",
    "Player can perform a zip using Sliding Powder"
)

roll_bonk_zip = Macro(
    can_zip & hammer_roll & obs_vhard,
    "Roll Bonk Zip",
    "Player can perform a zip with a bonk into an enemy while using Hammer Roll"
)

bunstrike_zip = Macro(
    can_zip & can_bunstrike_zip & bunny_strike,
    "Bunstrike Zip",
    "Player can perform a zip with Bunny Strike"
)

whirl_bonk = Macro(
    bunny_whirl & itm_hard,
    "Whirl Bonk",
    "Player can perform a whirl bonk by hitting an enemy with Bunny Whirl with high falling speed"
)

whirl_bonk_cancel = Macro(
    whirl_bonk & ((bunny_amulet & itm_hard) | obs_vhard),
    "Whirl Bonk Cancel",
    "Player can cancel a whirl bonk by using Bunny Amulet"
)

slide_jump_bunstrike = Macro(
    bunny_strike & intermediate,
    "Slide Jump Bunstrike",
    "Player can perform a Bunny Strike after jumping during a slide for additional height"
)

slide_jump_bunstrike_cancel = Macro(
    slide_jump_bunstrike & bunny_amulet & itm_hard,
    "Slide Jump Bunstrike Cancel",
    "Player can cancel a slide jump bunstrike by using Bunny Amulet"
)

downdrill_semisolid_clip = Macro(
    can_semi_solid_clip & piko_hammer_leveled,
    "Downdrill Semisolid Clip",
    "Player can clip through semisolid floors by performing a downdrill attack"
)

two_tile_downdrill_semisolid_clip = Macro(
    downdrill_semisolid_clip & obs_ext,
    "2 Tile Downdrill Semisolid Clip",
    "Player can clip through semisolid floors by performing a downdrill attack with a 2 tile ceiling"
)

eight_tile_wall_jump = Macro(
    (
        (intermediate & (hard | rules.Has(ItemName.wall_jump)))
        | rules.Has(ItemName.rabi_slippers)
        | rules.Has(ItemName.air_jump)
    ),
    "8 Tile Wall Jump",
    "Player can climb up an 8 tile high corridor using wall jumps"
)

one_tile_zip = Macro(
    slide_zip,
    "1 Tile Zip",
    "Player can slide zip through a 1 tile high ceiling"
)

two_tile_zip = Macro(
    slide_zip & adv_vhard,
    "2 Tile Zip",
    "Player can slide zip through a 2 tile high ceiling"
)

three_tile_zip = Macro(
    slide_zip & hard,
    "3 Tile Zip",
    "Player can slide zip through a 3 tile high ceiling"
)

four_tile_zip = Macro(
    slide_zip & hard,
    "4 Tile Zip",
    "Player can slide zip through a 4 tile high ceiling"
)

five_tile_zip = Macro(
    rules.Has(ItemName.rabi_slippers) & slide_zip & adv_vhard,
    "5 Tile Zip",
    "Player can slide zip through a 5 tile high ceiling"
)

five_tile_wall_climb = Macro(
    (
        rules.HasAny(ItemName.air_jump, ItemName.air_dash)
        | (adv_vhard & rules.Has(ItemName.rabi_slippers) & HasEnoughAmuletFoodRule(1))
        | (adv_ext & rules.Has(ItemName.wall_jump) & HasEnoughAmuletFoodRule(2) & (bunny_amulet | stupid))
        | (obs_stupid & can_do_boring_tricks & HasEnoughAmuletFoodRule(6))
    ),
    "5 Tile Wall Climb",
    "Player can climb up a wall that is 5 tiles high"
)

five_tile_wall_climb_bunstrike = Macro(
    (
        (rules.Has(ItemName.rabi_slippers) & slide_jump_bunstrike)
        | (adv_ext & slide_jump_bunstrike_cancel & HasEnoughAmuletFoodRule(2))
    ),
    "5 Tile Wall Climb Bunstrike",
    "Player can climb up a wall that is 5 tiles high using Bunny Strike"
)

rules_by_logic_key: dict[str, Macro | rules.Rule[RabiRibiWorldBase]] = {
    "HARD": hard,
    "V_HARD": vhard,
    "EXTREME": extreme,
    "STUPID": stupid,
    "ITM": intermediate,
    "ITM_HARD": itm_hard,
    "ITM_VHARD": itm_vhard,
    "ADV": advanced,
    "ADV_HARD": adv_hard,
    "ADV_VHARD": adv_vhard,
    "ADV_EXT": adv_ext,
    "ADV_STUPID": adv_stupid,
    "OBSCURE": obscure,
    "OBS_HARD": obs_hard,
    "OBS_VHARD": obs_vhard,
    "OBS_EXT": obs_ext,
    "OBS_STUPID": obs_stupid,
    "BORING": can_do_boring_tricks,
    "BLOCK_CLIP": can_block_clip,
    "POST_GAME": can_enter_post_game,
    "POST_IRISU": can_enter_post_irisu,
    "HALLOWEEN": can_enter_halloween,
    "PLURKWOOD": can_enter_plurkwood,
    "WARP_DESTINATION": can_enter_warp_destination,
    "BUNNY_STRIKE": bunny_strike,
    "BUNNY_WHIRL": bunny_whirl,
    "AIR_DASH": air_dash,
    "HAMMER_ROLL": hammer_roll,
    "DARKNESS": darkness,
    "UNDERWATER": underwater,
    "CARROT_SHOOTER": carrot_shooter,
    "EVENT_WARP": can_use_event_warps,
    "PROLOGUE_TRIGGER": rules.True_(), # Open Mode is always enabled in AP
    "NONE": rules.True_(),
    "IMPOSSIBLE": rules.False_(),
    "WALL_JUMP_LV2": wall_jump_lv2,
    "HAMMER_ROLL_LV3": hammer_roll_lv3,
    "AIR_DASH_LV3": air_dash_lv3,
    "SPEED_BOOST_LV3": speed_boost_lv3,
    "BUNNY_AMULET": bunny_amulet,
    "BUNNY_AMULET_LV2": bunny_amulet_lv2,
    "BUNNY_AMULET_LV3": bunny_amulet_lv3,
    "BUNNY_AMULET_LV4": bunny_amulet_lv4,
    "PIKO_HAMMER_LEVELED": piko_hammer_leveled,
    "CARROT_BOMB_ENTRY": carrot_bomb_entry,
    "CARROT_SHOOTER_ENTRY": carrot_shooter_entry,
    "CHARGE_CARROT_SHOOTER_ENTRY" : charge_carrot_shooter_entry,
    "COCOA_1": cocoa_1,
    "KOTRI_1": kotri_1,
    "ASHURI_2": ashuri_2,
    "BOSS_KEKE_BUNNY": boss_keke_bunny,
    "BOSS_RIBBON": boss_ribbon,
    "TM_CICINI": rules.Has(ItemName.cicini_recruit),
    "TM_SAYA": rules.Has(ItemName.saya_recruit),
    "TM_SYARO": rules.Has(ItemName.syaro_recruit),
    "TM_PANDORA": rules.Has(ItemName.pandora_recruit),
    "TM_LILITH": rules.Has(ItemName.lilith_recruit),
    "TM_VANILLA": rules.Has(ItemName.vanilla_recruit),
    "TM_CHOCOLATE": rules.Has(ItemName.chocolate_recruit),
    "TM_MIRIAM": rules.Has(ItemName.miriam_recruit),
    "TM_RUMI": rules.Has(ItemName.rumi_recruit),
    "TM_IRISU": rules.Has(ItemName.irisu_recruit),
    "3TM": TownMemberCountRule(3),
    "15TM": TownMemberCountIrisuRule(),
    "ITEM_MENU": item_menu,
    "CHAPTER_1": chapter_1,
    "CHAPTER_2": chapter_2,
    "CHAPTER_3": chapter_3,
    "CHAPTER_4": chapter_4,
    "CHAPTER_5": chapter_5,
    "CHAPTER_6": chapter_6,
    "CHAPTER_7": chapter_7,
    "CONSUMABLE_USE": consumable_use,
    "AMULET_FOOD": HasEnoughAmuletFoodRule(1),
    "2_AMULET_FOOD": HasEnoughAmuletFoodRule(2),
    "3_AMULET_FOOD": HasEnoughAmuletFoodRule(3),
    "4_AMULET_FOOD": HasEnoughAmuletFoodRule(4),
    "6_AMULET_FOOD": HasEnoughAmuletFoodRule(6),
    "MANY_AMULET_FOOD": many_amulet_food,
    "BOOST": boost,
    "BOOST_MANY": boost_many,
    "BOOST_BORING": boost_boring,
    "HAMMER_ROLL_ZIP": hammer_roll_zip,
    "SLIDE_ZIP": slide_zip,
    "ROLL_BONK_ZIP": roll_bonk_zip,
    "BUNSTRIKE_ZIP": bunstrike_zip,
    "WHIRL_BONK": whirl_bonk,
    "WHIRL_BONK_CANCEL": whirl_bonk_cancel,
    "SLIDE_JUMP_BUNSTRIKE": slide_jump_bunstrike,
    "SLIDE_JUMP_BUNSTRIKE_CANCEL": slide_jump_bunstrike_cancel,
    "DOWNDRILL_SEMISOLID_CLIP": downdrill_semisolid_clip,
    "2TILE_DOWNDRILL_SEMISOLID_CLIP": two_tile_downdrill_semisolid_clip,
    "8TILE_WALLJUMP": eight_tile_wall_jump,
    "EXPLOSIVES": explosives,
    "EXPLOSIVES_ENEMY": explosives_enemy,
    "SPEED1": speed1,
    "SPEED2": speed2,
    "SPEED3": speed3,
    "SPEED5": speed5,
    "1TILE_ZIP": one_tile_zip,
    "2TILE_ZIP": two_tile_zip,
    "3TILE_ZIP": three_tile_zip,
    "4TILE_ZIP": four_tile_zip,
    "5TILE_ZIP": five_tile_zip,
    "5TILE_WALL_CLIMB": five_tile_wall_climb,
    "5TILE_WALL_CLIMB_BUNSTRIKE": five_tile_wall_climb_bunstrike
}
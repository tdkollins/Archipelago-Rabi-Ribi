"""This module represents option defintions for Rabi-Ribi"""
from dataclasses import dataclass

from Options import PerGameCommonOptions, Toggle

class OpenMode(Toggle):
    """Gain access to chapter 1 areas without needing to complete the prologue"""
    display_name = "Open Mode"

class RandomizeHammer(Toggle):
    """If set to false, the hammer is at the default location"""
    display_name = "Randomize Hammer"

@dataclass
class RabiRibiOptions(PerGameCommonOptions):
    """Rabi Ribi Options Definition"""
    open_mode: OpenMode
    randomize_hammer: RandomizeHammer

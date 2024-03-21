"""This module represents option defintions for Rabi-Ribi"""
from dataclasses import dataclass

from Options import PerGameCommonOptions, Toggle

class OpenMode(Toggle):
    """Gain access to chapter 1 areas without needing to complete the prologue"""
    display_name = "Open Mode"

@dataclass
class RabiRibiOptions(PerGameCommonOptions):
    """Rabi Ribi Options Definition"""
    open_mode: OpenMode

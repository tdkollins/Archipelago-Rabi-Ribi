from typing import Union
from settings import Group, FilePath, UserFolderPath

class RabiRibiSettings(Group):
    class GameInstallationPath(UserFolderPath):
        """
        The installation folder of the game.
        """
        description = "Rabi-Ribi Installation Path"

    class UTPackPath(FilePath):
        """
        The Poptracker pack for Rabi-Ribi.
        """
        description = "Rabi-Ribi Poptracker Path"
        required = False

    game_installation_path: GameInstallationPath = GameInstallationPath("C:/Program Files (x86)/Steam/steamapps/common/Rabi-Ribi")
    ut_pack_path : Union[UTPackPath, str] = UTPackPath()
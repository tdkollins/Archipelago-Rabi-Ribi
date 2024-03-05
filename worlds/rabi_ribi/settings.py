import settings

class RabiRibiSettings(settings.Group):
    class GameInstallationPath(settings.UserFolderPath):
        """
        The installation folder of the game from a default steam installation
        """
    game_installation_path: GameInstallationPath = GameInstallationPath("C:/Program Files (x86)/Steam/steamapps/common/Rabi-Ribi")

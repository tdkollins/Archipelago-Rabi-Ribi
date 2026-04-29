from typing import ClassVar

from test.bases import WorldTestBase
from ..constants import GAME_NAME


class RabiRibiTestBase(WorldTestBase):
    game = GAME_NAME
    player: ClassVar[int] = 1

from . import RabiRibiTestBase
from ..names import ItemName

class GoalTestEggRounding(RabiRibiTestBase):
    options = {
        "max_number_of_easter_eggs": 19,
        "percentage_of_easter_eggs": 75
    }

    def test_egg_rounding(self) -> None:
        """
        Ensure that egg requirements are rounded down.
        """
        self.assertBeatable(False)
        for _ in range(14):
            item = self.get_item_by_name(ItemName.easter_egg)
            self.collect(item)
        self.assertBeatable(True)
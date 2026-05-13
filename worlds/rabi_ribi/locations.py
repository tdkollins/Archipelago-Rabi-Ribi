from BaseClasses import Location
from .constants import GAME_NAME, BASE_ID
from .data import data, LocationData
from .options import RabiRibiOptions

class RabiRibiLocation(Location):
    game: str = GAME_NAME

all_locations: dict[str, int] = {location.name: BASE_ID + location.id for location in data.locations}
lookup_location_id_to_name: dict[int, str] = {code: name for name, code in all_locations.items()}
location_groups: dict[str, set[str]] = data.create_location_groups()

@staticmethod
def _location_filter(options: RabiRibiOptions, location: LocationData) -> bool:
    if not bool(options.include_plurkwood.value) and location.requires_plurkwood:
        return False

    if not bool(options.include_warp_destination.value) and location.requires_warp_destination:
        return False

    if not bool(options.include_post_game.value) and location.requires_post_game:
        return False

    if not bool(options.include_post_irisu.value) and location.requires_post_irisu:
        return False

    if not bool(options.include_halloween.value) and location.requires_halloween:
        return False
    return True

@staticmethod
def setup_locations(options: RabiRibiOptions) -> dict[str, int]:
    return {location.name: BASE_ID + location.id for location in data.locations if _location_filter(options, location)}

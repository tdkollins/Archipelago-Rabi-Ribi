from worlds.LauncherComponents import Component, Type, components, launch_subprocess
from .constants import GAME_NAME

def launch_client():
    """Launch a Rabi-Ribi client instance"""
    from worlds.rabi_ribi.client.client import launch
    launch_subprocess(launch, name="RabiRibiClient")

components.append(
    Component(
        "Rabi-Ribi Client",
        func=launch_client,
        game_name=GAME_NAME,
        component_type=Type.CLIENT,
        supports_uri=True
    )
)
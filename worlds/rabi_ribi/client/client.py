from typing import Optional
import asyncio
import colorama
import pymem

from CommonClient import (
    CommonContext,
    get_base_parser,
    logger,
    server_loop,
    gui_enabled,
)
from worlds.rabi_ribi.client.memory_io import RabiRibiMemoryIO

class RabiRibiContext(CommonContext):
    """Rabi Ribi Game Context"""
    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.game = "Rabi-Ribi"
        self.items_handling = 0b001  # only items from other worlds
        self.rr_interface = RabiRibiMemoryIO()
        self.location_name_to_id = None
        self.location_id_to_name = None
        self.item_name_to_id = None
        self.item_id_to_name = None

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            asyncio.create_task(self.send_msgs([{"cmd": "GetDataPackage", "games": ["Rabi-Ribi"]}]))
        elif cmd == "DataPackage":
            self.location_name_to_id = args["data"]["games"]["Rabi-Ribi"]["location_name_to_id"]
            self.location_id_to_name = {v: k for k, v in self.location_name_to_id.items()}
            self.item_name_to_id = args["data"]["games"]["Rabi-Ribi"]["item_name_to_id"]
            self.item_id_to_name = {v: k for k, v in self.item_name_to_id.items()}
            location_ids = [loc_id for loc_id in self.location_id_to_name.keys()]
            asyncio.create_task(self.send_msgs([{
                "cmd": "LocationScouts",
                "locations": location_ids
            }]))
        elif cmd == "LocationInfo":
            # finished recieving location packets?
            if self.location_id_to_name and len(self.location_id_to_name) == len(self.locations_info):
                from worlds.rabi_ribi.client.patch import patch_map_files
                patch_map_files(self)

async def rabi_ribi_watcher(ctx: RabiRibiContext):
    logger.info("Waiting for connection to Rabi Ribi")
    while not ctx.exit_event.is_set():
        # if not ctx.rr_interface.is_connected():
            # await ctx.rr_interface.connect(ctx.exit_event)
        try:
            # logger.info(ctx.locations_info)
            pass
        except pymem.exception.ProcessNotFound:  # Rabi Ribi Process closed?
            # attempt to reconnect at the top of the loop
            continue
        await asyncio.sleep(1)


def launch():
    """
    Launch a client instance (wrapper / args parser)
    """
    async def main(args):
        """
        Launch a client instance (threaded)
        """
        ctx = RabiRibiContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="rabi ribi server loop")
        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()
        watcher = asyncio.create_task(
            rabi_ribi_watcher(ctx),
            name="RabiRibiProgressionWatcher"
        )
        await ctx.exit_event.wait()
        await watcher
        await ctx.shutdown()

    parser = get_base_parser(description="Rabi-Ribi Client")
    args, _ = parser.parse_known_args()

    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()

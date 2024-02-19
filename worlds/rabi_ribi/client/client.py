from typing import Optional, List
import asyncio
import colorama
import pymem
import ast

from CommonClient import (
    CommonContext,
    get_base_parser,
    logger,
    server_loop,
    gui_enabled,
)
from worlds.rabi_ribi.client.memory_io import RabiRibiMemoryIO
from worlds.rabi_ribi.logic_helpers import convert_existing_rando_name_to_ap_name
from NetUtils import NetworkItem

class RabiRibiContext(CommonContext):
    """Rabi Ribi Game Context"""
    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.game = "Rabi-Ribi"
        self.items_handling = 0b001  # only items from other worlds
        self.rr_interface = RabiRibiMemoryIO()
        self.location_name_to_ap_id = None
        self.location_ap_id_to_name = None
        self.item_name_to_ap_id = None
        self.item_ap_id_to_name = None
        self.location_coordinates_to_ap_location_name, self.item_name_to_rabi_ribi_id = \
            self.read_location_coordinates_and_rr_item_ids()
        # TODO: store on disconnect.
        self.received_items_index = 0
        self.gift_item_queue = asyncio.Queue()  # Items queued up to give to the player.

    def read_location_coordinates_and_rr_item_ids(self):
        """
        This method retrieves the location coordinates of each item from
        locations_items.txt, and dumps it in a mapping for later use.

        It also retrieves the rabi ribi item ids for each item and dumps
        that in a seperate map for later use.

        This is a slightly modified version of the code found in
        worlds.rabi_ribi.existing_randomizer.visualizer.load_item_locs()
        """
        coordinate_to_location_name = {}
        # TODO: will have to store the current id on disconnect
        item_name_to_rabi_ribi_item_id = {
            "Attack Up": 223,
            "MP Up": 287,
            "Regen Up": 351,
            "HP Up": 159,
            "Pack Up": 415
        }
        with open("worlds/rabi_ribi/existing_randomizer/locations_items.txt", "r", encoding="utf-8") as f:
            reading = False
            for line in f:
                if '===Items===' in line or '===ShufflableGiftItems===' in line:
                    reading = True
                    continue
                elif '===' in line:
                    reading = False
                    continue
                if not reading: continue
                l = line
                if '//' in line:
                    l = l[:l.find('//')]
                l = l.strip()
                if len(l) == 0: continue
                coords, areaid, rabi_ribi_item_id, name = (x.strip() for x in l.split(':'))

                # Set location coordinate to location name mapping
                area_id = int(areaid)
                x, y = ast.literal_eval(coords)
                ap_name = convert_existing_rando_name_to_ap_name(name)
                coordinate_to_location_name[(area_id, x, y)] = convert_existing_rando_name_to_ap_name(name)

                # Set item name to rabi ribi item id mapping
                item_name_to_rabi_ribi_item_id[ap_name] = rabi_ribi_item_id

        return coordinate_to_location_name, item_name_to_rabi_ribi_item_id

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            asyncio.create_task(self.send_msgs([{"cmd": "GetDataPackage", "games": ["Rabi-Ribi"]}]))
        elif cmd == "DataPackage":
            self.location_name_to_ap_id = args["data"]["games"]["Rabi-Ribi"]["location_name_to_id"]
            self.location_ap_id_to_name = {v: k for k, v in self.location_name_to_ap_id.items()}
            self.item_name_to_ap_id = args["data"]["games"]["Rabi-Ribi"]["item_name_to_id"]
            self.item_ap_id_to_name = {v: k for k, v in self.item_name_to_ap_id.items()}
            location_ids = [loc_id for loc_id in self.location_ap_id_to_name.keys()]
            asyncio.create_task(self.send_msgs([{
                "cmd": "LocationScouts",
                "locations": location_ids
            }]))
        elif cmd == "LocationInfo":
            # finished recieving location packets?
            if self.location_ap_id_to_name and len(self.location_ap_id_to_name) == len(self.locations_info):
                from worlds.rabi_ribi.client.patch import patch_map_files
                patch_map_files(self)
        elif cmd == "ReceivedItems":
            if args["index"] > self.received_items_index:
                asyncio.create_task(self.queue_items(args["items"]))

    async def queue_items(self, items: List[NetworkItem]):
        """
        Queue item(s) to give to the player

        :List[NetworkItem] items: the items to queue
        """
        for item in items:
            await self.gift_item_queue.put(item)

    async def give_item(self, item: NetworkItem):
        """
        Give an item to the player

        :NetworkItem item: The item to give to the player
        """
        item_name = self.item_ap_id_to_name[item.item]
        rabi_ribi_item_id = self.item_name_to_rabi_ribi_id[item_name]
        self.rr_interface.give_item(rabi_ribi_item_id)
        if item_name in ["Attack Up", "MP Up", "HP Up", "Regen Up", "Pack Up"]:
            self.item_name_to_rabi_ribi_id[item_name] -= 1
        self.received_items_index += 1

async def rabi_ribi_watcher(ctx: RabiRibiContext):
    """
    Client loop, watching the rabi ribi game process.
    Handles game hook attachments, checking locations, giving items, etc.

    :RabiRibiContext ctx: The Rabi Ribi Client context instance.
    """
    logger.info("Waiting for connection to Rabi Ribi")
    while not ctx.exit_event.is_set():
        if not ctx.rr_interface.is_connected():
            await ctx.rr_interface.connect(ctx.exit_event)
        # make sure to check if the server is connected
        try:
            await check_for_locations(ctx)
            if not ctx.gift_item_queue.empty() and not ctx.rr_interface.is_player_frozen():
                await ctx.give_item(await ctx.gift_item_queue.get())
        except pymem.exception.ProcessNotFound:  # Rabi Ribi Process closed?
            # attempt to reconnect at the top of the loop
            continue
        await asyncio.sleep(1)

async def check_for_locations(ctx: RabiRibiContext):
    """
    This method checks if the player coordinates overlaps with any location checks.
    If it is, it will update the locations_checked set to include the location
    (if its not already included).

    :RabiRibiContext ctx: The Rabi Ribi Client context instance.
    """
    if ctx.rr_interface.is_player_frozen():  # Game paused or just got item
        # Check if we're in a 1 tile radius of an item
        player_coordinates = ctx.rr_interface.read_player_tile_position()
        for coordinates in [
            # area_id, x, y. The player is 2 tiles high and 1 tile wide.
            (player_coordinates[0], player_coordinates[1], player_coordinates[2]),
            (player_coordinates[0], player_coordinates[1] - 1, player_coordinates[2]),
            (player_coordinates[0], player_coordinates[1] + 1, player_coordinates[2]),
            (player_coordinates[0], player_coordinates[1], player_coordinates[2] - 1),
            (player_coordinates[0], player_coordinates[1], player_coordinates[2] + 1),
            (player_coordinates[0], player_coordinates[1] - 1, player_coordinates[2] - 1),
            (player_coordinates[0], player_coordinates[1] + 1, player_coordinates[2] - 1),
            (player_coordinates[0], player_coordinates[1], player_coordinates[2] - 2),
        ]:
            if coordinates in ctx.location_coordinates_to_ap_location_name:
                ap_location_name = ctx.location_coordinates_to_ap_location_name[coordinates]
                location_id = ctx.location_name_to_ap_id[ap_location_name]
                if location_id not in ctx.locations_checked:
                    ctx.locations_checked.add(location_id)
                    await ctx.send_msgs([{"cmd": 'LocationChecks', "locations": ctx.locations_checked}])
                    break

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

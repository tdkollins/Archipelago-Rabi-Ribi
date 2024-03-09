from typing import Optional, List
import ast
import asyncio
import colorama
import os
import pymem
from pathlib import Path

from CommonClient import (
    CommonContext,
    get_base_parser,
    logger,
    server_loop,
    gui_enabled,
)
from worlds.rabi_ribi import RabiRibiWorld
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
        self.location_coordinates_to_ap_location_name, self.item_name_to_rabi_ribi_item_id = \
            self.read_location_coordinates_and_rr_item_ids()

        self.received_items_index = 0
        self.recieved_rabi_ribi_item_ids = []

        # TODO: make sure queue syncs if game quits before all items sent out
        self.gift_item_queue = asyncio.Queue()  # Items queued up to give to the player.
        self.custom_seed_subdir = None # populated when we have the unique seed ID

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
            self.patch_if_recieved_all_data()

        if cmd == "RoomInfo":
            self.custom_seed_subdir = f"{RabiRibiWorld.settings.game_installation_path}/custom/{args['seed_name']}-{self.auth}"
            if not os.path.isdir(self.custom_seed_subdir):
                os.mkdir(self.custom_seed_subdir)
                Path(self.custom_seed_subdir + "/items_received.txt").touch()
            else:
                self.read_items_recieved_from_storage()
            asyncio.create_task(self.send_msgs([{"cmd": "GetDataPackage", "games": ["Rabi-Ribi"]}]))

        elif cmd == "DataPackage":
            self.location_name_to_ap_id = args["data"]["games"]["Rabi-Ribi"]["location_name_to_id"]
            self.location_ap_id_to_name = {v: k for k, v in self.location_name_to_ap_id.items()}
            self.item_name_to_ap_id = args["data"]["games"]["Rabi-Ribi"]["item_name_to_id"]
            self.item_ap_id_to_name = {v: k for k, v in self.item_name_to_ap_id.items()}
            location_ids = [loc_id for loc_id in self.location_ap_id_to_name.keys()]
            # Only request location data if there doesnt appear to be patched game files already
            if not os.path.isfile(f"{self.custom_seed_subdir}/area0.map"):
                asyncio.create_task(self.send_msgs([{
                    "cmd": "LocationScouts",
                    "locations": location_ids
                }]))

        elif cmd == "LocationInfo":
            self.patch_if_recieved_all_data()

        elif cmd == "ReceivedItems":
            if args["index"] > self.received_items_index:
                self.write_items_recieved_to_memory_and_storage(args["items"])

    def patch_if_recieved_all_data(self):
        """
        Requirements for patching:
            - All LocationInfo packages recieved - requested only if patch files dont exist.
            - DataPackage package recieved (id_to_name maps and name_to_id maps are popualted)
            - Connection package recieved (slot number populated)
            - RoomInfo package recieved (seed name populated)
        """
        if self.custom_seed_subdir and self.slot and self.location_ap_id_to_name and \
            len(self.location_ap_id_to_name) == len(self.locations_info):
                # Patch the map files if we haven't done so already
                if not os.path.isfile(f"{self.custom_seed_subdir}/area0.map"):
                    from worlds.rabi_ribi.client.patch import patch_map_files
                    patch_map_files(self)

    async def give_item(self):
        """
        Give an item to the player. This method will always give the oldest
        item that the player has recieved from AP, but not in game yet.

        :NetworkItem item: The item to give to the player
        """
        # find the first item id that the player has not recieved yet
        cur_item_id = 0
        for item_id in self.recieved_rabi_ribi_item_ids:
            cur_item_id = item_id
            if not self.rr_interface.does_player_have_item_id(cur_item_id):
                break
        self.rr_interface.give_item(cur_item_id)

    def convert_network_item_to_rabi_ribi_item_id(self, item: NetworkItem):
        """
        This method converts a network item into a given rabi ribi item id.
        If the item has multiple valid ids, it will decrement the value for the next instance
        such that they are unique.
        """
        item_name = self.item_ap_id_to_name[item.item]
        rabi_ribi_item_id = self.item_name_to_rabi_ribi_item_id[item_name]
        if item_name in ["Attack Up", "MP Up", "HP Up", "Regen Up", "Pack Up"]:
            self.item_name_to_rabi_ribi_item_id[item_name] -= 1
        return rabi_ribi_item_id

    def write_items_recieved_to_memory_and_storage(self, items):
        """
        This method writes the recieved items into permanent storage.
        This is used to sync items during a save load.
        """
        item_ids = []
        for item in items:
            item_id = self.convert_network_item_to_rabi_ribi_item_id(item)
            item_ids.append(item_id)
        self.recieved_rabi_ribi_item_ids += item_ids

        # Write to permanent storage as well so that we can load during a new session.
        with open(self.custom_seed_subdir + "/items_received.txt", "a", encoding="utf-8") as fp:
            for item_id in item_ids:
                fp.write(str(item_id) + "\n")
                self.received_items_index += 1

    def read_items_recieved_from_storage(self):
        """
        This method reads the recieved items from storage into memory.
        this is used to sync items during a save load.
        """
        self.recieved_rabi_ribi_item_ids = []
        with open(self.custom_seed_subdir + "/items_received.txt", "r", encoding="utf-8") as fp:
            for item_id in fp:
                item_id = int(item_id.strip())
                self.recieved_rabi_ribi_item_ids.append(item_id)
                if 96 <= item_id <= 319:
                    self.decrement_current_potion_item_id(item_id)

    def decrement_current_potion_item_id(self, item_id):
        """
        Sets the id of the next potion found. This function should be called
        when a new potion is found and we need to decrement the current id.
        """
        if 96 <= item_id <= 159:
            self.item_name_to_rabi_ribi_item_id["HP Up"] -= 1
        elif 160 <= item_id <= 223:
            self.item_name_to_rabi_ribi_item_id["Attack Up"] -= 1
        elif 224 <= item_id <= 287:
            self.item_name_to_rabi_ribi_item_id["MP Up"] -= 1
        elif 288 <= item_id <= 351:
            self.item_name_to_rabi_ribi_item_id["Regen Up"] -= 1
        else:
            self.item_name_to_rabi_ribi_item_id["Pack Up"] -= 1

    def is_item_queued(self):
        """
        To determine if we have any items to give, look at the last recieved item and check if the player
        currently has it in their inventory
        """
        if self.recieved_rabi_ribi_item_ids:
            return not self.rr_interface.does_player_have_item_id(self.recieved_rabi_ribi_item_ids[-1])
        return False

    def is_in_shaft(self):
        """
        Returns true if the player is in the starting shaft. We want to avoid giving them items
        if this is the case since its pitch black so you cant see any of the items that you get.
        """
        area_id, x, y = self.rr_interface.read_player_tile_position()
        return area_id == 0 and \
            110 <= x <= 112 and \
            36 <= y <= 91

    async def wait_until_out_of_shaft(self):
        """
        Waits until the player is out of the starting shaft, plus a few extra seconds for safety.
        If the player isnt in the starting shaft, returns immediatly.
        """
        if not self.is_in_shaft():
            return
        while self.is_in_shaft() and not self.exit_event.is_set():
            await asyncio.sleep(1)
        if not self.exit_event.is_set():
            await asyncio.sleep(5)

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
            await ctx.wait_until_out_of_shaft()
            await check_for_locations(ctx)
            if not ctx.rr_interface.is_player_frozen() and ctx.is_item_queued():
                await ctx.give_item()

            # Fallback if player collected items while the client was disconnected.
            #   Make sure the player never has an exclamation point in their inventory.
            #   (or else they wont be able to see/collect any other exclamation point)
            ctx.rr_interface.remove_exclamation_point_from_inventory()

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
                await remove_exclamation_point(ctx, coordinates)
                break

async def remove_exclamation_point(ctx: RabiRibiContext, coordinates):
    while ctx.rr_interface.is_player_frozen():
        await asyncio.sleep(0.25)
    ctx.rr_interface.remove_exclamation_point_from_inventory()
    ctx.rr_interface.remove_item_from_in_memory_map(coordinates[0], coordinates[1], coordinates[2])
    from worlds.rabi_ribi.client.patch import remove_item_from_map
    remove_item_from_map(ctx, coordinates[0], coordinates[1], coordinates[2])

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

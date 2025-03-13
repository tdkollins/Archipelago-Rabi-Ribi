from typing import Dict, Optional, Set, Tuple
import ast
import asyncio
import colorama
import os
import pymem
from pathlib import Path
import time
import hashlib

from CommonClient import (
    CommonContext,
    get_base_parser,
    logger,
    server_loop,
    gui_enabled,
)
from NetUtils import ClientStatus

from worlds.rabi_ribi import RabiRibiWorld
from worlds.rabi_ribi.client.memory_io import RabiRibiMemoryIO
from worlds.rabi_ribi.names import ItemName
from worlds.rabi_ribi.utility import (
    load_text_file,
    convert_existing_rando_name_to_ap_name
)

STRANGE_BOX_ITEM_ID = 30
PBPB_BOX_ITEM_ID = 58

class RabiRibiContext(CommonContext):
    """Rabi Ribi Game Context"""
    def __init__(self, server_address: Optional[str], password: Optional[str]) -> None:
        super().__init__(server_address, password)
        self.game = "Rabi-Ribi"
        self.items_handling = 0b001  # only items from other worlds
        self.rr_interface = RabiRibiMemoryIO()
        self.location_ids = None
        self.location_name_to_ap_id = None
        self.location_ap_id_to_name = None
        self.item_name_to_ap_id = None
        self.item_ap_id_to_name = None
        self.location_coordinates_to_ap_location_name, self.item_name_to_rabi_ribi_item_id = \
            self.read_location_coordinates_and_rr_item_ids()

        self.ap_location_name_to_location_coordinates: Dict[str, Tuple[int, int, int]] = {}
        for area, v in self.location_coordinates_to_ap_location_name.items():
            for (x, y), name in v.items():
                self.ap_location_name_to_location_coordinates[name] = (area, x, y)

        self.state_giving_item = False
        self.collected_eggs: Set[Tuple[int,int,int]] = set()
        self.last_received_item_index = -1
        self.seed_name = None
        self.slot_data = None

        # populated when we have the unique seed ID
        self.custom_seed_subdir = None
        self.seed_player = None
        self.seed_player_id = None

        self.time_since_last_paused = time.time()
        self.time_since_main_menu = time.time()
        self.time_since_last_item_obtained = time.time()
        self.time_since_last_warp_menu = time.time()
        self.time_since_last_costume_menu = time.time()
        
        self.items_received_rabi_ribi_ids = []
        self.obtained_items_queue = asyncio.Queue()

        self.critical_section_lock = asyncio.Lock()

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
        item_name_to_rabi_ribi_item_id = {
            ItemName.attack_up: 223,
            ItemName.mp_up: 287,
            ItemName.regen_up: 351,
            ItemName.hp_up: 159,
            ItemName.pack_up: 415
        }

        # location_items.txt contains 3 sets of items:
        #   - Items, for items that can be found lying around.
        #   - ShufflableGiftItems, for items normally gifted to the player, but have a location
        #     added by the randomizer.
        #   - AdditionalItems, for items that are either bought at the shop, or given to the player
        #     but have not been added as a location to the randomizer
        # While Items and ShufflableGiftItems have are stored in the same format, AdditionalItems
        # does not contain location information, so we need to read them separately.
        locations_items_file = os.path.join('existing_randomizer', 'locations_items.txt')
        f = load_text_file(locations_items_file)
        reading_items = False
        reading_additional_items = False
        for line in f.splitlines():
            if '===Items===' in line or '===ShufflableGiftItems===' in line:
                reading_items = True
                continue
            elif '===AdditionalItems===' in line:
                reading_additional_items = True
                continue
            elif '===' in line:
                reading_items = False
                reading_additional_items = False
                continue
            if reading_items:
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
                if area_id not in coordinate_to_location_name:
                    coordinate_to_location_name[area_id] = {(x, y): ap_name}
                else:
                    coordinate_to_location_name[area_id][(x, y)] = ap_name

                # Set item name to Rabi Ribi item ID mapping
                item_id = int(rabi_ribi_item_id)
                item_name_to_rabi_ribi_item_id[ap_name] = item_id
            if reading_additional_items:
                l = line
                if '//' in line:
                    l = l[:l.find('//')]
                l = l.strip()
                if len(l) == 0: continue
                name, rabi_ribi_item_id = (x.strip() for x in line.split(':'))

                # Only set item name to Rabi Ribi item ID mapping
                ap_name = convert_existing_rando_name_to_ap_name(name)
                item_id = int(rabi_ribi_item_id)
                item_name_to_rabi_ribi_item_id[ap_name] = item_id

        return coordinate_to_location_name, item_name_to_rabi_ribi_item_id

    async def server_auth(self, password_requested: bool = False):
        if password_requested and not self.password:
            await super().server_auth(password_requested)
        await self.get_username()
        await self.send_connect()

    def on_package(self, cmd: str, args: dict):
        if cmd == "Connected":
            self.location_ids = set(args["missing_locations"] + args["checked_locations"])
            self.slot_data = args["slot_data"]

            asyncio.create_task(self.send_msgs([{"cmd": "GetDataPackage", "games": ["Rabi-Ribi"]}]))

            # if we dont have the seed name from the RoomInfo packet, wait until we do.
            while not self.seed_name:
                time.sleep(1)
            self.seed_player = f"{self.seed_name}-{self.auth}"
            self.seed_player_id = str(hashlib.sha256(self.seed_player.encode()).hexdigest()[:7])
            self.custom_seed_subdir = f"{RabiRibiWorld.settings.game_installation_path}/custom/{self.seed_player}"

        if cmd == "ReceivedItems":
            asyncio.create_task(self.set_received_rabi_ribi_item_ids())

        if cmd == "RoomInfo":
            self.seed_name = args['seed_name']

        elif cmd == "DataPackage":
            if not self.location_ids:
                # Connected package not recieved yet, wait for datapackage request after connected package
                return
            self.location_name_to_ap_id = args["data"]["games"]["Rabi-Ribi"]["location_name_to_id"]
            self.location_name_to_ap_id = {
                name: loc_id for name, loc_id in 
                self.location_name_to_ap_id.items() if loc_id in self.location_ids
            }
            self.location_ap_id_to_name = {v: k for k, v in self.location_name_to_ap_id.items()}
            self.item_name_to_ap_id = args["data"]["games"]["Rabi-Ribi"]["item_name_to_id"]
            self.item_ap_id_to_name = {v: k for k, v in self.item_name_to_ap_id.items()}

            # Only request location data if there doesnt appear to be patched game files already
            if not os.path.isfile(f"{self.custom_seed_subdir}/area0.map"):
                asyncio.create_task(self.send_msgs([{
                    "cmd": "LocationScouts",
                    "locations": self.location_ids
                }]))

        elif cmd == "LocationInfo":
            if len(args["locations"]) > 1:
                # initial request on first connect.
                self.patch_if_recieved_all_data()
            else:
                # request after an item is obtained
                asyncio.create_task(self.obtained_items_queue.put(args["locations"][0]))

    def client_recieved_initial_server_data(self):
        """
        This method waits until the client finishes the initial conversation with the server.
        This means:
            - All LocationInfo packages recieved - requested only if patch files dont exist.
            - DataPackage package recieved (id_to_name maps and name_to_id maps are popualted)
            - Connection package recieved (slot number populated)
            - RoomInfo package recieved (seed name populated)
        """
        return (
            self.custom_seed_subdir and
            self.slot and
            self.location_ap_id_to_name
        )

    async def wait_for_initial_connection_info(self):
        """
        This method waits until the client finishes the initial conversation with the server.
        See client_recieved_initial_server_data for wait requirements.
        """
        if self.client_recieved_initial_server_data():
            return

        logger.info("Waiting for connect from server...")
        while not self.client_recieved_initial_server_data() and not self.exit_event.is_set():
            await asyncio.sleep(1)
        if not self.exit_event.is_set():
            # wait an extra second to process data
            await asyncio.sleep(1)
            logger.info("Received initial data from server!")
            logger.info("****************************************************")
            logger.info("Please press F5 on the main menu and start scenario:")
            logger.info("       %s - %s",
                self.seed_name,
                self.auth)
            logger.info("****************************************************")
            logger.info("Softlocked? Disable the Strange Box in your inventory and unpause to open the warp menu!")

    def patch_if_recieved_all_data(self):
        """
        See client_recieved_initial_server_data for wait requirements.
        """
        if self.client_recieved_initial_server_data():
            # Patch the map files if we haven't done so already
            self.custom_seed_subdir = f"{RabiRibiWorld.settings.game_installation_path}/custom/{self.seed_name}-{self.auth}"
            if not os.path.isdir(self.custom_seed_subdir):
                os.mkdir(self.custom_seed_subdir)
            if not os.path.isfile(f"{self.custom_seed_subdir}/area0.map"):
                from worlds.rabi_ribi.client.patch import patch_map_files
                patch_map_files(self)

    async def give_item(self):
        """
        Give an item to the player. This method will always give the oldest
        item that the player has recieved from AP, but not in game yet.

        :NetworkItem item: The item to give to the player
        """
        self.last_received_item_index = self.rr_interface.get_last_received_item_index()

        # Find the first item ID that the player has not recieved yet
        remaining_items = self.items_received_rabi_ribi_ids[self.last_received_item_index:]
        skipped_items, cur_item_id = next(((idx, item_id) for idx, item_id in enumerate(remaining_items) if item_id != -1), (-1, -1))

        if cur_item_id > 0:
            self.rr_interface.give_item(cur_item_id)
            self.rr_interface.set_last_received_item_index(self.last_received_item_index + skipped_items + 1)
            await asyncio.sleep(1)
            await self.wait_until_out_of_item_receive_animation()

    async def set_received_rabi_ribi_item_ids(self):
        async with self.critical_section_lock:
            self.items_received_rabi_ribi_ids = []
            potion_ids = {
                ItemName.attack_up: 193, # Subtract 30, as those IDs are reserved for super / hyper attack modes
                ItemName.mp_up: 287,
                ItemName.regen_up: 351,
                ItemName.hp_up: 159,
                ItemName.pack_up: 415
            }

            if not self.item_ap_id_to_name:
                await self.wait_for_initial_connection_info()

            for network_item in self.items_received:
                item_name = self.item_ap_id_to_name[network_item.item]
                if item_name == ItemName.nothing:
                    self.items_received_rabi_ribi_ids.append(-1)
                elif item_name in potion_ids:
                    self.items_received_rabi_ribi_ids.append(potion_ids[item_name])
                    potion_ids[item_name] -= 1
                elif item_name == ItemName.easter_egg:
                    if network_item.player == self.slot:
                        location_name = self.location_ap_id_to_name[network_item.location]
                        egg_coordinates = self.ap_location_name_to_location_coordinates[location_name]
                        self.collected_eggs.add(egg_coordinates)
                else:
                    self.items_received_rabi_ribi_ids.append(
                        int(self.item_name_to_rabi_ribi_item_id[item_name]))

    def is_item_queued(self):
        """
        To determine if we have any items to give, look at the last recieved item and check if the player
        currently has it in their inventory
        """
        if self.items_received:
            for item_id in self.items_received_rabi_ribi_ids[::-1]:
                if item_id != -1:
                    return not self.rr_interface.does_player_have_item_id(item_id)
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

    async def handle_egg_changes(self):
        if self.location_name_to_ap_id is None:
            return
        player_current_eggs = self.rr_interface.get_collected_eggs()
        for (area, x, y) in player_current_eggs:
            if (area, x, y) not in self.collected_eggs:
                self.collected_eggs.add((area, x, y))
                if area in self.location_coordinates_to_ap_location_name and (x, y) in self.location_coordinates_to_ap_location_name[area]:
                    location_name = self.location_coordinates_to_ap_location_name[area][(x, y)]
                    location_id = self.location_name_to_ap_id[location_name]
                    if location_id not in self.locations_checked:
                        self.locations_checked.add(location_id)
                        await self.send_msgs([{"cmd": 'LocationChecks', "locations": self.locations_checked}])

    def is_player_paused(self):
        paused = self.rr_interface.is_player_paused()
        if paused:
            self.time_since_last_paused = time.time()
        return paused
    
    def is_player_in_warp_menu(self):
        in_warp_menu = self.rr_interface.is_in_warp_menu()
        if in_warp_menu:
            self.time_since_last_warp_menu = time.time()
        return in_warp_menu

    def is_player_in_costume_menu(self):
        in_costume_menu = self.rr_interface.is_in_costume_menu()
        if in_costume_menu:
            self.time_since_last_costume_menu = time.time()
        return in_costume_menu

    def in_state_where_can_give_items(self):
        cur_time = time.time()
        return (
            (cur_time - self.time_since_last_paused >= 2) and
            (cur_time - self.time_since_last_warp_menu >= 5.5) and
            (cur_time - self.time_since_last_costume_menu >= 2) and
            not self.rr_interface.is_player_frozen() and
            self.is_item_queued()
        )

    def in_state_where_should_open_warp_menu(self):
        cur_time = time.time()
        return (
            (cur_time - self.time_since_last_paused >= .5) and
            not self.rr_interface.is_player_frozen() and
            not self.is_item_queued() and
            self.rr_interface.get_item_state(STRANGE_BOX_ITEM_ID) == -1
        )

    async def watch_for_menus(self):
        """
        Run this on a faster loop. We want to detect pauses really fast since players
        can reload a save really fast with quick save reload. We want to make sure that
        we dont give items too soon after a save load since this lags the game hard.
        """
        while self.rr_interface.is_connected() and not self.exit_event.is_set():
            self.is_player_paused()
            self.is_player_in_warp_menu()
            self.is_player_in_costume_menu()
            await asyncio.sleep(0.1)

    def is_on_main_menu(self):
        on_main_menu = self.rr_interface.is_on_main_menu()
        if on_main_menu:
            self.time_since_main_menu = time.time()
        return on_main_menu

    def open_warp_menu(self):
        # Reenable the Strange Box first.
        self.rr_interface.set_item_state(STRANGE_BOX_ITEM_ID, 1)
        self.rr_interface.open_warp_menu()

    def find_closest_item_location(self):
        """
        Finds the closest location to the player for the purpose of finding which
        check they just cleared. Returns None if it cannot find any location within
        10 tiles.

        :returns int, (int, int, int): the ap id of the closest location and the coordinates of it
        """
        # Just recieved an item, mark the closet location as the one found
        area_id, x, y = self.rr_interface.read_player_tile_position()
        closest_location_id = None
        closest_location_coordinates = None
        closest_distance = 9999

        if self.location_name_to_ap_id is None:
            return None, None
        if area_id not in self.location_coordinates_to_ap_location_name:
            return None, None
        for coordinate_entry, location_name in self.location_coordinates_to_ap_location_name[area_id].items():
            if location_name not in self.location_name_to_ap_id:
                # location not included with the enabled settings.
                continue
            distance = abs(x - coordinate_entry[0]) + abs(y - coordinate_entry[1])
            if distance < closest_distance:
                closest_distance = distance
                closest_location_id = self.location_name_to_ap_id[location_name]
                closest_location_coordinates = (area_id, *coordinate_entry)
        if closest_distance < 10:
            return closest_location_id, closest_location_coordinates
        return None, None

    async def wait_until_out_of_item_receive_animation(self):
        """
        Waits until the player is outside the item receive animation, and then returns.
        """
        while self.rr_interface.is_in_item_receive_animation() and not self.exit_event.is_set():
            await asyncio.sleep(0.1)

    def reset_client_state(self):
        """
        Reset client back to default values
        """
        self.locations_checked = set()
        self.location_ids = None
        self.location_name_to_ap_id = None
        self.location_ap_id_to_name = None
        self.item_name_to_ap_id = None
        self.item_ap_id_to_name = None
        self.location_coordinates_to_ap_location_name, self.item_name_to_rabi_ribi_item_id = \
            self.read_location_coordinates_and_rr_item_ids()

        self.ap_location_name_to_location_coordinates: Dict[str, Tuple[int, int, int]] = {}
        for area, v in self.location_coordinates_to_ap_location_name.items():
            for (x, y), name in v.items():
                self.ap_location_name_to_location_coordinates[name] = (area, x, y)

        self.state_giving_item = False
        self.collected_eggs = set()
        self.last_received_item_index = -1
        self.seed_name = None
        self.slot_data = None

        self.custom_seed_subdir = None
        self.seed_player = None
        self.seed_player_id = None

        self.time_since_last_paused = time.time()
        self.time_since_main_menu = time.time()
        self.time_since_last_item_obtained = time.time()
        self.time_since_last_warp_menu = time.time()
        self.time_since_last_costume_menu = time.time()

        self.items_received_rabi_ribi_ids = []
        self.obtained_items_queue = asyncio.Queue()

async def rabi_ribi_watcher(ctx: RabiRibiContext):
    """
    Client loop, watching the rabi ribi game process.
    Handles game hook attachments, checking locations, giving items, etc.

    :RabiRibiContext ctx: The Rabi Ribi Client context instance.
    """
    await ctx.wait_for_initial_connection_info()
    while not ctx.exit_event.is_set():
        if not ctx.server:
            # client disconnected from server
            ctx.reset_client_state()
            await ctx.wait_for_initial_connection_info()
        if not ctx.rr_interface.is_connected():
            logger.info("Waiting for connection to Rabi Ribi")
            await ctx.rr_interface.connect(ctx.exit_event)
            asyncio.create_task(ctx.watch_for_menus())
        try:
            while True:
                if not ctx.server:
                    break
                await asyncio.sleep(0.5)
                if ctx.exit_event.is_set():
                    break
                if ctx.seed_player_id is None:
                    continue
                if not ctx.rr_interface.is_on_correct_scenerio(ctx.seed_player_id):
                    continue
                if ctx.is_on_main_menu():
                    continue
                if time.time() - ctx.time_since_main_menu < 4:
                    continue
                break
            if ctx.exit_event.is_set():
                break
            if not ctx.server:
                continue
            await ctx.wait_until_out_of_shaft()

            cur_time = time.time()

            await ctx.handle_egg_changes()
            await check_for_locations(ctx)

            if ctx.in_state_where_should_open_warp_menu():
                ctx.open_warp_menu()

            if ctx.in_state_where_can_give_items():
                await ctx.give_item()

            # Fallback if player collected items while the client was disconnected.
            #   Make sure the player never has an exclamation point in their inventory.
            #   (or else they wont be able to see/collect any other exclamation point)
            if cur_time - ctx.time_since_last_item_obtained > 7:
                ctx.rr_interface.remove_exclamation_point_from_inventory()

            if ctx.rr_interface.get_number_of_eggs_collected() >= 5:
                ctx.finished_game = True
                await ctx.send_msgs([{"cmd": "StatusUpdate", "status": ClientStatus.CLIENT_GOAL}])

        except Exception as err:  # Rabi Ribi Process closed?
            logger.warning("*******************************")
            logger.warning("Encountered error. Please post a message to the Rabi-Ribi thread on the AP discord")
            logger.warning("*******************************")
            logger.exception(str(err))
            # attempt to reconnect at the top of the loop
            continue
        await asyncio.sleep(0.5)

async def check_for_locations(ctx: RabiRibiContext):
    """
    This method checks if the player coordinates overlaps with any location checks.
    If it is, it will update the locations_checked set to include the location
    (if its not already included).

    :RabiRibiContext ctx: The Rabi Ribi Client context instance.
    """
    # Game paused or just got item
    if ctx.rr_interface.is_in_item_receive_animation():
        ap_location_id, coordinates = ctx.find_closest_item_location()
        if not ap_location_id:
            # logger.warning("Detected item obtained, but unable to find location.")
            return
        if ap_location_id not in ctx.locations_checked:
            ctx.locations_checked.add(ap_location_id)
            await ctx.send_msgs([{"cmd": 'LocationChecks', "locations": ctx.locations_checked}])

        # scout the location and delete it from the map if its an explanation point
        asyncio.create_task(ctx.send_msgs([{
            "cmd": "LocationScouts",
            "locations": [ap_location_id]
        }]))
        ctx.time_since_last_item_obtained = time.time()

        try:
            network_item = await asyncio.wait_for(ctx.obtained_items_queue.get(), timeout=15)
            if network_item.player != ctx.slot or (network_item.player == ctx.slot and ctx.item_names.lookup_in_game(network_item.item) == "Nothing"):
                await remove_exclamation_point(ctx, coordinates)
        except TimeoutError:
            logger.warning("Never received response to scout request for ap_location_id %d", ap_location_id)

async def remove_exclamation_point(ctx: RabiRibiContext, coordinates):
    ctx.rr_interface.remove_item_from_in_memory_map(coordinates[0], coordinates[1], coordinates[2])
    from worlds.rabi_ribi.client.patch import remove_item_from_map
    remove_item_from_map(ctx, coordinates[0], coordinates[1], coordinates[2])
    while ctx.rr_interface.is_player_frozen():
        await asyncio.sleep(0.25)
    ctx.rr_interface.remove_exclamation_point_from_inventory()

def launch():
    """
    Launch a client instance (wrapper / args parser)
    """
    async def main(args):
        """
        Launch a client instance (threaded)
        """
        ctx = RabiRibiContext(args.connect, args.password)
        ctx.server_task = asyncio.create_task(server_loop(ctx), name="Rabi-Ribi Server Loop")

        if gui_enabled:
            ctx.run_gui()
        ctx.run_cli()

        watcher = asyncio.create_task(
            rabi_ribi_watcher(ctx),
            name="Rabi-Ribi Progression Watcher"
        )
        await ctx.exit_event.wait()
        await watcher
        await ctx.shutdown()

    parser = get_base_parser(description="Rabi-Ribi Client")
    args, _ = parser.parse_known_args()

    colorama.init()
    asyncio.run(main(args))
    colorama.deinit()

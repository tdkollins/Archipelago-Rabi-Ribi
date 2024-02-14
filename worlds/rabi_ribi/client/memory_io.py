"""
This module defines a class RabiRibiMemoryIO, which attaches
itself to an open Rabi Ribi process and reads/writes memory
in realtime. This is used to:
 - Recognize when a player gets an item
 - Write items to the player's inventory
 - Handle in game flags when a player recieves an AP item.
 - Modify map data loaded into memory.
 - etc... 
"""
import struct
import psutil

from pymem import pymem
import asyncio
import keystone

from CommonClient import logger

OFFSET_PLAYER_X = int(0x0103469C)
OFFSET_PLAYER_Y = int(0x013AFDB4)
OFFSET_GIVE_ITEM_FUNC = int(0x15A90)
TILE_LENGTH = 64

class RabiRibiMemoryIO():
    """
    RabiRibiMemoryIO serves as an interface for reading/writing memory to and from
    a rabi-ribi game instance.
    """

    def __init__(self):
        self.rr_mem = None
        self.rr_process_id = None
        self.addr_injected_give_item_entrypoint = None

    def is_connected(self):
        if self.rr_mem is None:
            return False
        if not psutil.pid_exists(self.rr_process_id):  # confirm the process is still running
            logger.info("Rabi Ribi connection lost.")
            self.rr_process_id = None
            self.rr_mem = None
            return False
        return True

    async def connect(self, exit_event: asyncio.Event):
        logger.info("Waiting for connection to Rabi Ribi game instance...")
        while not exit_event.is_set():
            try:
                self.rr_mem = pymem.Pymem("rabiribi.exe")
                self.rr_process_id = self.rr_mem.process_id
                logger.info("Successfully connected to Rabi Ribi Game.")
                return
            except pymem.exception.ProcessNotFound:
                await asyncio.sleep(3)

    async def allocate(self):
        self.addr_injected_give_item_entrypoint = self.rr_mem.allocate(12) # 3 instructions.

    async def _read_word(self, offset):
        """
        Read 4 bytes of data at <base_process_address> + offset and return it.

        :int offset: the offset to read data from.
        :returns: The data represented as a byte string
        """
        data = self.rr_mem.read_bytes(self.rr_mem.base_address + offset, 4)
        return data

    async def _read_float(self, offset):
        """
        Read a word at the specified offset, and interpret it as a float.

        :int offset: the offset to read data from.
        :returns: The data represented as a float.
        """
        data = self._read_word(offset)
        return struct.unpack("f", data)[0]

    async def read_player_tile_position(self):
        """
        Read the player (x,y) and convert it to tile (x,y).

        :returns: The tile position represented as an integer 2-tuple
        """
        player_x = self._read_float(OFFSET_PLAYER_X)
        player_y = self._read_float(OFFSET_PLAYER_Y)
        return (int(player_x // TILE_LENGTH), int(player_y // TILE_LENGTH))

    async def give_item(self, item_id):
        """
        Run the in-game give-item function. We do this by injecting our own code
        which calls the func (setting the correct parameters in the registers),
        and then running a thread at the startpoint of our injected code.

        :int item_id: the rabi-ribi id of the item to give to the player
        :returns: None
        """
        addr_give_item_func = self.rr_mem.base_address + OFFSET_GIVE_ITEM_FUNC
        # keystone interprets injected entrypoint as 0. We subtract the injected entrypoint address
        #   so we can math the actual offset we want from the real 0 addr.
        addr_give_item_func = addr_give_item_func - self.addr_injected_give_item_entrypoint

        # convert our assembly code to bytes
        architecture = keystone.KS_ARCH_X86
        mode = keystone.KS_MODE_32
        endianess = keystone.KS_MODE_LITTLE_ENDIAN
        ks = keystone.Ks(architecture, mode | endianess)
        injected_call_func_code = f"mov ecx,{item_id}; call {addr_give_item_func}; ret".encode()
        injected_call_func_code, _ = ks.asm(injected_call_func_code)
        injected_call_func_code = bytes(injected_call_func_code)

        # write our code to memory
        self.rr_mem.write_bytes(
            self.addr_injected_give_item_entrypoint, 
            injected_call_func_code, 
            len(injected_call_func_code)
        )

        # start a thread at the entrypoint of our injected code
        self.rr_mem.start_thread(self.addr_injected_give_item_entrypoint)

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
        self.rr_interface = RabiRibiMemoryIO()

async def rabi_ribi_watcher(ctx: RabiRibiContext):
    logger.info("Waiting for connection to Rabi Ribi")
    while not ctx.exit_event.is_set():
        if not ctx.rr_interface.is_connected():
            await ctx.rr_interface.connect(ctx.exit_event)
        try:
            pass
        except pymem.exception.ProcessNotFound:
            # Process was closed, attempt to reconnect at the top of the loop
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

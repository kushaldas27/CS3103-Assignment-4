import asyncio
from GameNetAPI.GameNetAPI import GameNetAPI


async def main():
    gameNetAPI = GameNetAPI("server")

    await gameNetAPI.server_serve("127.0.0.1", 4444)

    # keep the server running until manually stopped
    await asyncio.Event().wait()


asyncio.run(main())

import asyncio

from GameNetAPI.GameNetServerAPI import GameNetServer


async def main():
    server = GameNetServer("10.0.0.1", 4444)
    await server.setup()

    # keep the server running until manually stopped
    await asyncio.Event().wait()


asyncio.run(main())

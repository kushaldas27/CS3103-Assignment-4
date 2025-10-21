import asyncio

from GameNetAPI.GameNetServerAPI import GameNetServer


async def main():
    server = GameNetServer("127.0.0.1", 1234)
    await server.setup()

    # keep the server running until manually stopped
    await asyncio.Event().wait()


asyncio.run(main())

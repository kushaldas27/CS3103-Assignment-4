import asyncio

from GameNetAPI.GameNetReceiver import GameNetReceiver


async def main():
    server = GameNetReceiver("127.0.0.1", 1234)
    await server.setup()

    # keep the server running until manually stopped
    await asyncio.Event().wait()


asyncio.run(main())

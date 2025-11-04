import asyncio
from GameNetAPI.GameNetAPI import GameNetAPI


async def main():
    server = GameNetAPI("server")

    await server.server_serve("127.0.0.1", 4444)

    print("Server is successfully running")

    # keep the server running until manually stopped
    await asyncio.Event().wait()


asyncio.run(main())

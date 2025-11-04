import asyncio
from GameNetAPI.GameNetAPI import GameNetAPI

async def main():
    client = GameNetAPI("client")
    
    await client.server_serve("127.0.0.1", 4444)

    print("Client is successfully running")

asyncio.run(main())

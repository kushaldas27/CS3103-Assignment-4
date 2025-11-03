import asyncio
from GameNetAPI.GameNetAPI import GameNetAPI

async def main():
    
    gameNetAPI = GameNetAPI()

    await gameNetAPI.client_connect("127.0.0.1", 4444)

asyncio.run(main())
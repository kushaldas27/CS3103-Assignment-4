import asyncio
import random
from GameNetAPI.GameNetAPI import GameNetAPI


def generateMetrics():
    return

async def main():
    
    gameNetAPI = GameNetAPI("client")

    await gameNetAPI.client_connect("127.0.0.1", 4444)

    for i in range(30):
        # Randomizer to determine between reliable (1) and unreliable (0)
        isReliable = random.randint(0,1) 

        print("Packet isReliable:", isReliable)
        
        data =  "This is a test message " + str(i)
        gameNetAPI.client_send_data(data.encode(), isReliable)

        await asyncio.sleep(1)

asyncio.run(main())
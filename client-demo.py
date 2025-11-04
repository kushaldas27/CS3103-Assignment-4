import asyncio
import random
from GameNetAPI.GameNetAPI import GameNetAPI


def generateMetrics():
    return

async def main():
    
    gameNetAPI = GameNetAPI("client")

    await gameNetAPI.client_connect("127.0.0.1", 4444)

    while True:
        # Randomizer to determine between reliable (1) and unreliable (0)
        isReliable = random.randint(0,1) 

        print("Packet isReliable:", isReliable)
        
        data =  input("Enter data to send to server: ")
        gameNetAPI.client_send_data(data.encode(), isReliable)



asyncio.run(main())
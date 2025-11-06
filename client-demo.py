import asyncio
import random
from GameNetAPI.GameNetAPI import GameNetAPI


def generateMetrics():
    return

async def main():
    
    gameNetAPI = GameNetAPI("client")

    await gameNetAPI.client_connect("10.0.0.1", 4444)

    sent_reliable = 0
    sent_unreliable = 0

    for i in range(100):
        # Randomizer to determine between reliable (1) and unreliable (0)
        isReliable = random.randint(0,1) 

        print("Packet isReliable:", isReliable)
        
        if isReliable == 1:
            sent_reliable += 1
        else:
            sent_unreliable += 1

        data =  "This is a test message " + str(i)
        gameNetAPI.client_send_data(data.encode(), isReliable)
        await asyncio.sleep(0.1)

       

    # final data packet
    data = f"END {sent_reliable} {sent_unreliable}"
    gameNetAPI.client_send_data(data.encode(), 1)
    await asyncio.sleep(0.1)
    print("sent last packet")
asyncio.run(main())

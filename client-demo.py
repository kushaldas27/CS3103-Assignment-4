import asyncio
import random
from GameNetAPI.GameNetAPI import GameNetAPI
import time


def generateMetrics():
    return

async def main():
    
    gameNetAPI = GameNetAPI("client")

    await gameNetAPI.client_connect("10.0.0.1", 4444)

    sent_reliable = 0
    sent_unreliable = 0
    start_time = time.time()

    for i in range(100):
        # Randomizer to determine between reliable (1) and unreliable (0)
        if i == 99:
            isReliable = 1
        else:
            isReliable = random.randint(0,1) 

        print("Packet isReliable:", isReliable)
        
        if isReliable == 1:
            sent_reliable += 1
        else:
            sent_unreliable += 1

        data =  "This is a test message " + str(i)
        gameNetAPI.client_send_data(data.encode(), isReliable)
        await asyncio.sleep(0.1)
    
    await asyncio.sleep(0.1)

    duration = time.time() - start_time
       

    # final data packet
    data = f"END {sent_reliable} {sent_unreliable} {duration}"
    gameNetAPI.client_send_data(data.encode(), 1)
    await asyncio.sleep(0.1)
    print("sent last packet")

asyncio.run(main())

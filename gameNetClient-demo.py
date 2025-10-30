import asyncio

from GameNetAPI.GameNetClientAPI import GameNetClient

async def main():
    client = GameNetClient("10.0.0.1", 4444)
    await client.setup()

    #TODO execute client.run() 
    #Upon running, client will randomize stream id and sent random data which will be encapsulated in Packet Class

    client.run()
    # while True:
    #     client.run()
    #     await asyncio.sleep(1)  # wait 1 second or else it will overwhelm the server

asyncio.run(main())

import asyncio

from GameNetAPI.GameNetClientAPI import GameNetClient

async def main():
    client = GameNetClient("127.0.0.1", 1234)
    await client.setup()

    #TODO execute client.run() 
    #Upon running, client will randomize stream id and sent random data which will be encapsulated in Packet Class

    while True:
        client.run()
        await asyncio.sleep(1)  # wait 1 second or else it will overwhelm the server

        # client.send_data(client.reliable_stream, b"This is a reliable message")
        # await asyncio.sleep(1)


asyncio.run(main())

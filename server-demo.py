import asyncio
from GameNetAPI.GameNetAPI import GameNetAPI
from GameNetAPI.Packet import Packet


async def main():
    gameNetAPI = GameNetAPI("server")

    await gameNetAPI.server_serve("127.0.0.1", 4444)

    def logPackets(packet : Packet):
        print(f"Server received Packet ID: {packet.getPacketId()}, Reliable: {'RELIABLE' if packet.isReliable else 'UNRELIABLE'}")

    gameNetAPI.setPacketLogger(logPackets)

    # keep the server running until manually stopped
    await asyncio.Event().wait()


asyncio.run(main())

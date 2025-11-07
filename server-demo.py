import asyncio
from GameNetAPI.GameNetAPI import GameNetAPI

async def main():
    gameNetAPI = GameNetAPI("server")

    await gameNetAPI.server_serve("10.0.0.1", 4444)

    # Callback to handle info from API
    def handle_stats(info):
        """
        This receives info dicts from the API:
        - 'packet' type for each packet received
        - 'summary' type for END packet statistics
        """
        if info["type"] == "packet":
            print(f"Packet ID: {info['packet_id']}, Reliable: {info['reliable']}, Latency: {info['latency_ms']:.2f} ms")
        elif info["type"] == "summary":
            print("=== SUMMARY ===")
            print(f"Reliable Packet Delivery Ratio: {info['received_reliable']}/{info['sent_reliable']} = {info['ratio_reliable']:.2f}%")
            print(f"Reliable Throughput: {info['reliable_throughput']:.2f} bytes/s")
            print(f"Reliable Average Latency: {info['reliable_avg_latency']:.2f} ms")
            print(f"Reliable Jitter: {info['jitter_reliable']:.2f} ms")
            print(f"Unreliable Packet Delivery Ratio: {info['received_unreliable']}/{info['sent_unreliable']} = {info['ratio_unreliable']:.2f}%")
            print(f"Unreliable Throughput: {info['unreliable_throughput']:.2f} bytes/s")
            print(f"Unreliable Average Latency: {info['unreliable_avg_latency']:.2f} ms")
            print(f"Unreliable Jitter: {info['jitter_unreliable']:.2f} ms")
            print("================")

    # Set API logger callback
    gameNetAPI.setPacketLogger(handle_stats)
   
   # keep the server running until manually stopped
    await asyncio.Event().wait()


asyncio.run(main())

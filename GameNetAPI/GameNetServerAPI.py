import pickle
import struct
import aioquic.asyncio as quic_asyncio
import aioquic.quic.events as events
from GameNetAPI.Packet import Packet
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration
from aioquic.quic.logger import QuicFileLogger


class GameNetServerProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # buffer per stream for partial reads
        self.stream_buffers = {}


    def handleReliableStream(self, event: events.QuicEvent):
        
        buf = self.stream_buffers.get(event.stream_id, b"") + event.data
        while len(buf) >= 4:  # need at least 4 bytes for length
            packet_len = struct.unpack("!I", buf[:4])[0]
            if len(buf) < 4 + packet_len:
                break  # wait for more data
            packet_bytes = buf[4:4+packet_len]
            try:
                packet = pickle.loads(packet_bytes)
                self.logPackets(packet)
                print(f"Server received stream packet {packet.getPacketId()}: {packet.getData()} on stream {event.stream_id}")
            except pickle.UnpicklingError:
                print(f"[Stream {event.stream_id}] Invalid packet")
            buf = buf[4+packet_len:]

        self.stream_buffers[event.stream_id] = buf

        

        if event.data == b"PING": # Retransmission 
            self._quic.send_stream_data(event.stream_id, b"PONG", end_stream=False)
        else:
            self._quic.send_stream_data(event.stream_id, b"ACK", end_stream=False)
        self.transmit()

    
    def handleUnreliableStream(self, event: events.QuicEvent):
        try:
            packet = self.analyzePacket(event.data)
            self.logPackets(packet)
            print(f"Server received datagram packet {packet.getPacketId()}: {packet.getData()}")
        except pickle.UnpicklingError:
            print("Dropped invalid datagram packet")
        
    def quic_event_received(self, event: events.QuicEvent): # Action to take upon receiving events
        if isinstance(event, events.StreamDataReceived):
            self.handleReliableStream(event)

        elif isinstance(event, events.DatagramFrameReceived):
            self.handleUnreliableStream(event)
            

    def analyzePacket(self, packet_bytes):
        packet_object = pickle.loads(packet_bytes)
        return packet_object

    def logPackets(self, packet : Packet):

        packetNo = packet.getPacketId()
        roundTripTime = packet.getRTT()
        channelType = packet.isReliable
        sentTime = packet.getTimeStamp()

        return

class GameNetServer:
    def __init__(self, recv_ip: str, recv_port: int, certfile: str = "cert.pem", keyfile: str = "key.pem"):
        self.recv_ip = recv_ip 
        self.recv_port = recv_port 
        self.config = QuicConfiguration(is_client=False)
        self.config.max_datagram_frame_size = 65536

        quic_logger = QuicFileLogger("logs")
        self.config.quic_logger = quic_logger
        # The server must load a certificate and private key for QUIC/TLS to work.
        try:
            self.config.load_cert_chain(certfile, keyfile)
        except Exception:
            raise RuntimeError("Server TLS cert/key not found or invalid: place cert.pem and key.pem in the project directory")

        self.protocol = GameNetServerProtocol

        self.server = None

    async def setup(self):
        print(f"Server: starting on {self.recv_ip}:{self.recv_port}")
        self.server = await quic_asyncio.server.serve(
            host=self.recv_ip, port=self.recv_port, configuration=self.config, create_protocol=self.protocol
        )
        print("Server: started")

    # TODO: Implement a shutdown method to gracefully stop the server when needed

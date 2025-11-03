import ssl
import pickle
import datetime
import itertools
import struct
import logging
import aioquic.asyncio as quic_asyncio
import aioquic.quic.events as events
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration


class Packet:

    id_object = itertools.count()
    
    def __init__(self, data, isReliable):

        #### Headers of packet ####
        self.id = next(Packet.id_object) # Auto increment seq no of the packet
        self.data = data
        self.isReliable = isReliable
        self.timeStamp = datetime.datetime.now()
        pass

    def getPacketId(self): # Get the seq no of the packet
        return self.id

    def getData(self): # Get the data of the packet
        return self.data
    
    def getChannel(self): # Get the stream at which the packet has been sent to
        return self.channelType
    
    def getTimeStamp(self): # Get the time stamp at which the packet was created
        return self.timeStamp
    
    def getRTT(self): 
        duration = datetime.datetime.now() - self.timeStamp
        return duration
    
    def serialize(self) -> bytes:
        """
        Serialize packet with 4-byte length prefix for reliable streams.
        """
        packet_bytes = pickle.dumps(self)
        length_prefix = struct.pack("!I", len(packet_bytes))
        return length_prefix + packet_bytes


# Quic Protocol for client
class ClientGameNetProtocol(QuicConnectionProtocol):
    
    def quic_event_received(self, event: events.QuicEvent):
        if isinstance(event, events.StreamDataReceived):
            print(f"Server received on stream {event.stream_id}: {event.data}")

# Quic Protocol for server
class ServerGameNetProtocol(QuicConnectionProtocol):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # buffer per stream for partial reads
        self.stream_buffers = {}

        logging.basicConfig(
            filename="server.log",            
            level=logging.INFO,
        )

        self.logger = logging.getLogger("GameNetServer")

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

    def logPackets(self, packet: Packet):
        packet_id = packet.getPacketId()
        reliable = 'RELIABLE' if packet.isReliable else 'UNRELIABLE'
        rtt_ms = packet.getRTT().total_seconds() * 1000 if packet.getRTT() else 0.0
        sent_time = packet.getTimeStamp()

            
        self.logger.info(f"Packet ID: {packet_id}, Reliable: {reliable}, RTT: {rtt_ms:.2f} ms, Sent Time: {sent_time}")


class GameNetAPI:

    def __init__(self):

        # Set up QUIC configuration for client
        self.client_config = QuicConfiguration(is_client=True)
        self.client_config.verify_mode = ssl.CERT_NONE
        self.client_context = None
        self.client_protocol = None
        self.reliable_stream = None

        # Set up QUIC configuration for server
        self.server_config = QuicConfiguration(is_client=False)
        self.server_config.max_datagram_frame_size = 65536
        

    async def client_connect(self, target_ip: str, target_port: int):

        print(f"Client connecting to {target_ip}:{target_port}")
        
        self.client_context = quic_asyncio.client.connect(
            host=target_ip, port=target_port, configuration=self.client_config, create_protocol=ClientGameNetProtocol
        )
        self.protocol = await self.client_context.__aenter__()
        self.reliable_stream = self.protocol._quic.get_next_available_stream_id()
        
        print("Client connected successfully")
        return 
    
    async def server_serve(self, recv_ip: str, recv_port: int):
        
        try:
            self.server_config.load_cert_chain("cert.pem", "key.pem")
        except Exception:
            raise RuntimeError("Server TLS cert/key not found or invalid: place cert.pem and key.pem in the project directory")

        await quic_asyncio.server.serve(
            host=recv_ip, port=recv_port, configuration=self.server_config, create_protocol=ServerGameNetProtocol
        )

        print(f"Server: started on {recv_ip}:{recv_port}")
        return

    def client_send_data(self, data, isReliable: int):

        # Construct packet
        packet = Packet(data, isReliable)

        if self.client_context is None:
            raise RuntimeError("connection not established; call client_connect() first")

        if self.client_protocol is None:
            raise RuntimeError("protocol not established; call client_connect() first")

        packet_bytes = packet.serialize() if packet.isReliable else pickle.dumps(packet)
        if packet.isReliable:
            self.client_protocol._quic.send_stream_data(self.reliable_stream, packet_bytes, end_stream=False)
            self.client_protocol.transmit()
        else:
            self.client_protocol._quic.send_datagram_frame(packet_bytes)
            self.client_protocol.transmit()


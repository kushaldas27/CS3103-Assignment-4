import ssl
import pickle
import datetime
import itertools
import struct
import aioquic.asyncio as quic_asyncio
import aioquic.quic.events as events
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration


class Packet:

    id_object = itertools.count()
    
    def __init__(self, data, isReliable):

        #### Headers of packet ####
        if isReliable:
            self.id = next(Packet.id_object) # Auto increment seq no of the packet
        else:
            self.id = -1
        self.data = data
        self.isReliable = isReliable
        self.timeStamp = datetime.datetime.now()

    def getPacketId(self): # Get the seq no of the packet
        return self.id

    def getData(self): # Get the data of the packet
        return self.data
    
    def getChannel(self): # Get the stream at which the packet has been sent to
        return self.channelType
    
    def getTimeStamp(self): # Get the time stamp at which the packet was created
        return self.timeStamp
    
    def getLatency(self): # Deduct time packet with received - time packet was created
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
    def __init__(self, *args, packetLogger, **kwargs):
        super().__init__(*args, **kwargs)
        # buffer per stream for partial reads
        self.stream_buffers = {}
        self.packetLogger = packetLogger

        self.received_reliable = 0
        self.received_unreliable = 0
        self.latencies = []
        self.total_reliable_bytes = 0
        self.total_unreliable_bytes = 0
        self.total_latency_reliable = 0
        self.total_latency_unreliable = 0

        self.last_reliable_packet_time = 0
        self.last_unreliable_packet_time = 0
        self.reliable_packet_jitter = 0
        self.unreliable_packet_jitter = 0

    def handleReliableStream(self, event: events.QuicEvent):
        
        buf = self.stream_buffers.get(event.stream_id, b"") + event.data
        while len(buf) >= 4:  # need at least 4 bytes for length
            packet_len = struct.unpack("!I", buf[:4])[0]
            if len(buf) < 4 + packet_len:
                break  # wait for more data
            packet_bytes = buf[4:4+packet_len]
            try:
                packet = pickle.loads(packet_bytes)
                self.logPacket(packet)
                self.total_reliable_bytes += len(packet_bytes)
            except pickle.UnpicklingError:
                print(f"[Stream {event.stream_id}] Invalid packet")
            buf = buf[4+packet_len:]

        self.stream_buffers[event.stream_id] = buf

        # Send ACK back for reliable packet
        self._quic.send_stream_data(event.stream_id, b"ACK", end_stream=False)
        self.transmit()
        

    
    def handleUnreliableStream(self, event: events.QuicEvent):
        try:
            packet = self.analyzePacket(event.data)
            self.logPacket(packet)
            self.total_unreliable_bytes += len(event.data)
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

    def setPacketLogger(self, logger):
        self.packetLogger = logger

    def logPacket(self, packet: Packet):
        if packet.isReliable:
            self.received_reliable += 1
        else:
            self.received_unreliable += 1

        data = packet.getData().decode()
        latency_ms = packet.getLatency().total_seconds() * 1000 if packet.getLatency() else 0.0
        if packet.isReliable:
            self.total_latency_reliable += latency_ms
        elif not packet.isReliable:
            self.total_latency_unreliable += latency_ms
        packet_id = packet.getPacketId()

        if packet.isReliable:
            if self.last_reliable_packet_time == 0:
                self.last_reliable_packet_time = latency_ms
     
            else:
                difference = abs(latency_ms - self.last_reliable_packet_time)

                # Applying RFC 3550 jitter calculation
                self.reliable_packet_jitter += (difference - self.reliable_packet_jitter) / 16
                self.last_reliable_packet_time = latency_ms

        else:
            if self.last_unreliable_packet_time == 0:
                self.last_unreliable_packet_time = latency_ms
            
            else:
                difference = abs(latency_ms - self.last_unreliable_packet_time)
                # Applying RFC 3550 jitter calculation
                self.unreliable_packet_jitter += (difference - self.unreliable_packet_jitter) / 16
                self.last_unreliable_packet_time = latency_ms



        # Check for END packet
        if data.upper().startswith("END"):
            # The END packet itself is reliable; adjust count
            self.received_reliable -= 1

            sent_reliable = int(data.split(" ")[1])
            sent_unreliable = int(data.split(" ")[2])
            duration = float(data.split(" ")[3])

            reliable_throughput = self.total_reliable_bytes / duration
            unreliable_throughput = self.total_unreliable_bytes / duration
            reliable_avg_latency = self.total_latency_reliable / self.received_reliable
            unreliable_avg_latency = self.total_latency_unreliable / self.received_unreliable
            ratio_reliable = (self.received_reliable / sent_reliable) * 100 if sent_reliable else 0
            ratio_unreliable = (self.received_unreliable / sent_unreliable) * 100 if sent_unreliable else 0
            summary = {
                "type": "summary",
                "received_reliable": self.received_reliable,
                "sent_reliable": sent_reliable,
                "reliable_throughput": reliable_throughput,
                "unreliable_throughput": unreliable_throughput,
                "reliable_avg_latency":  reliable_avg_latency,
                "unreliable_avg_latency": unreliable_avg_latency,
                "jitter_reliable": self.reliable_packet_jitter,
                "jitter_unreliable": self.unreliable_packet_jitter,
                "ratio_reliable": ratio_reliable,
                "received_unreliable": self.received_unreliable,
                "sent_unreliable": sent_unreliable,
                "ratio_unreliable": ratio_unreliable
            }

            if self.packetLogger:
                self.packetLogger(summary)

            # Reset counters if needed
            self.received_reliable = 0
            self.received_unreliable = 0

        else:
            info = {
                "type": "packet",
                "packet_id": packet_id,
                "reliable": packet.isReliable,
                "latency_ms": latency_ms,
                "jitter": self.reliable_packet_jitter if packet.isReliable else self.unreliable_packet_jitter,
                "data": data
            }

            if self.packetLogger:
                self.packetLogger(info)


class GameNetAPI:

    def __init__(self, role: str):
        self.packetLogger = None

        if role == "client":
            # Set up QUIC configuration for client
            self.client_config = QuicConfiguration(is_client=True)
            self.client_config.verify_mode = ssl.CERT_NONE
            self.client_context = None
            self.client_protocol = None
            self.reliable_stream = None
        
        elif role == "server":
            # Set up QUIC configuration for server
            self.server_config = QuicConfiguration(is_client=False)
            self.server_config.max_datagram_frame_size = 65536
        

    def setPacketLogger(self, logger):
        self.packetLogger = logger
    
    def protocol_factory(self, *args, **kwargs):
        return ServerGameNetProtocol(*args, packetLogger=self.packetLogger, **kwargs)

    async def client_connect(self, target_ip: str, target_port: int):

        print(f"Client connecting to {target_ip}:{target_port}")
        
        self.client_context = quic_asyncio.client.connect(
            host=target_ip, port=target_port, configuration=self.client_config, create_protocol=ClientGameNetProtocol
        )
        self.client_protocol = await self.client_context.__aenter__()
        self.reliable_stream = self.client_protocol._quic.get_next_available_stream_id()
        
        print("Client connected successfully")
        return 
    
    async def server_serve(self, recv_ip: str, recv_port: int):
        
        try:
            self.server_config.load_cert_chain("cert.pem", "key.pem")
        except Exception:
            raise RuntimeError("Server TLS cert/key not found or invalid: place cert.pem and key.pem in the project directory")

        await quic_asyncio.server.serve(
            host=recv_ip, port=recv_port, configuration=self.server_config, create_protocol=self.protocol_factory
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

        if packet.getData().decode()[:3] == "END":
            self.client_protocol._quic.send_stream_data(self.reliable_stream, packet_bytes, end_stream=False)
            self.client_protocol.transmit()
        elif packet.isReliable:
            self.client_protocol._quic.send_stream_data(self.reliable_stream, packet_bytes, end_stream=False)
            self.client_protocol.transmit()
        else:
            self.client_protocol._quic.send_datagram_frame(packet_bytes)
            self.client_protocol.transmit()

       

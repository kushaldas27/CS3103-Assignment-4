import ssl

import random
import pickle
from Packet import Packet
import aioquic.asyncio as quic_asyncio
import aioquic.quic.events as events
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration


class GameNetClientProtocol(QuicConnectionProtocol):
    
    # Retransmission from server
    def quic_event_received(self, event: events.QuicEvent):
        if isinstance(event, events.StreamDataReceived):
            print(f"Client received on stream {event.stream_id}: {event.data}")

    #TODO deparse Packet Class 


class GameNetClient:
    def __init__(self, target_ip: str, target_port: int):

        #### CONFIGURATION FOR QUIC API ####
        self.target_ip = target_ip
        self.target_port = target_port
        self.config = QuicConfiguration(is_client=True)

        # for local testing with a self-signed cert, disable verification
        # this requires cert.pem and key.pem to be present in the project directory
        # the cert and private keys are generated with default values, no secrets involved
        # it is required because QUIC uses TLS for security
        self.config.verify_mode = ssl.CERT_NONE

        # Allow datagrams to be sent
        self.config.max_datagram_frame_size = 1200

        self.reliable_stream = None
        self.context = None  # need to manage context manually so that the 2 streams above can be used anywhere
        self.protocol = None  # this is established when client manages to connect to server

    async def setup(self):
        self.context = quic_asyncio.client.connect(
            host=self.target_ip, port=self.target_port, configuration=self.config, create_protocol=GameNetClientProtocol
        )
        self.protocol = await self.context.__aenter__()
        self.reliable_stream = self.protocol._quic.get_next_available_stream_id()

    async def teardown(self):
        if self.context is not None:
            await self.context.__aexit__(None, None, None)
            self.context = None
            self.protocol = None
            self.reliable_stream = None
            self.unreliable_stream = None

    def send_data(self, stream_id: int | None, data: bytes):
        if self.context is None:
            raise RuntimeError("connection not established; call setup() first")

        if self.protocol is None:
            raise RuntimeError("protocol not established; call setup() first")

        if stream_id is None:
            raise RuntimeError("stream ID is None")
        
        if stream_id == self.reliable_stream:
            # Reliable stream
            print("Client sending on RELIABLE stream")
            self.protocol._quic.send_stream_data(stream_id, data, end_stream=False)
            self.protocol.transmit()

        else:
            # Unreliable stream
            print("Client sending on UNRELIABLE stream")
            self.protocol._quic.send_datagram_frame(data)
            self.protocol.transmit()
        

    def ping(self):
        self.send_data(self.reliable_stream, b"PING")


    def constructPacket(self, data, isReliable):
        packet = Packet(data, isReliable)
        packet_bytes = pickle.dumps(packet)
        return packet_bytes


    def run(self):

        data = "This is a test message"

        for i in range(10):
            # Randomizer to determine between 0 (Unreliable) and 1 (Reliable)
            isReliable = random.randint(0,1) 

            packet = self.constructPacket(data, isReliable)
            
            if isReliable:
                self.send_data(self.reliable_stream, packet)
            else:
                self.send_data(1, packet)

        return
            


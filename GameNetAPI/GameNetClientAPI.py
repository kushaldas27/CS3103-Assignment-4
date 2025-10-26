import ssl

import aioquic.asyncio as quic_asyncio
import aioquic.quic.events as events
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration


class GameNetClientProtocol(QuicConnectionProtocol):
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

        self.reliable_stream = None
        self.unreliable_stream = None
        self.context = None  # need to manage context manually so that the 2 streams above can be used anywhere
        self.protocol = None  # this is established when client manages to connect to server

    async def setup(self):
        self.context = quic_asyncio.client.connect(
            host=self.target_ip, port=self.target_port, configuration=self.config, create_protocol=GameNetClientProtocol
        )
        self.protocol = await self.context.__aenter__()
        self.reliable_stream = self.protocol._quic.get_next_available_stream_id()
        self.unreliable_stream = self.protocol._quic.get_next_available_stream_id()

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

        if stream_id not in [self.reliable_stream, self.unreliable_stream]:
            raise RuntimeError("invalid stream ID")

        if stream_id is None:
            raise RuntimeError("stream ID is None")

        self.protocol._quic.send_stream_data(stream_id, data, end_stream=False)
        self.protocol.transmit()

    def ping(self):
        self.send_data(self.reliable_stream, b"PING")


    #TODO Set up randomizer

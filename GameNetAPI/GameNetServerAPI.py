import aioquic.asyncio as quic_asyncio
import aioquic.quic.events as events
from aioquic.asyncio.protocol import QuicConnectionProtocol
from aioquic.quic.configuration import QuicConfiguration


class GameNetServerProtocol(QuicConnectionProtocol):
    def quic_event_received(self, event: events.QuicEvent): # Action to take upon receiving events
        if isinstance(event, events.StreamDataReceived):
            print(f"Server received on stream {event.stream_id}: {event.data}")

            #TODO deparse Packet Class 
            self.analyzePacket()
            
            #TODO add logging (eg count latency eg)
            self.logPackets()

            if event.data == b"PING": # Retransmission 
                
                #TODO Set retransmission

                self._quic.send_stream_data(event.stream_id, b"PONG", end_stream=False)
            else:

                # TODO: change content of ACK according to application logic, like application sequence numbers

                self._quic.send_stream_data(event.stream_id, b"ACK", end_stream=False)

            self.transmit()

    def analyzePacket():
        return
    

    def logPackets():
        return
    

class GameNetServer:
    def __init__(self, recv_ip: str, recv_port: int, certfile: str = "cert.pem", keyfile: str = "key.pem"):
        self.recv_ip = recv_ip # Initialize ip 
        self.recv_port = recv_port # Initialize port
        self.config = QuicConfiguration(is_client=False)
        # The server must load a certificate and private key for QUIC/TLS to work.
        try:
            self.config.load_cert_chain(certfile, keyfile)
        except Exception:
            raise RuntimeError("Server TLS cert/key not found or invalid: place cert.pem and key.pem in the project directory")

        # protocol used to handle incoming events
        self.protocol = GameNetServerProtocol

        self.server = None

    async def setup(self):
        print(f"Server: starting on {self.recv_ip}:{self.recv_port}")
        self.server = await quic_asyncio.server.serve(
            host=self.recv_ip, port=self.recv_port, configuration=self.config, create_protocol=self.protocol
        )
        print("Server: started")

    # TODO: Implement a shutdown method to gracefully stop the server when needed

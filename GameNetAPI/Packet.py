import datetime
import itertools
import struct
import pickle

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
    
    def getLatency(self): 
        duration = datetime.datetime.now() - self.timeStamp
        return duration
    
    def serialize(self) -> bytes:
        """
        Serialize packet with 4-byte length prefix for reliable streams.
        """
        packet_bytes = pickle.dumps(self)
        length_prefix = struct.pack("!I", len(packet_bytes))
        return length_prefix + packet_bytes

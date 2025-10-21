import datetime
import itertools
import struct

class Packet:

    id_object = itertools.count()
    
    def __init__(self, data, isReliable):
        self.id = next(Packet.id_object)
        self.data = data
        self.channelType = 1 if isReliable else 0
        self.timeStamp = datetime.datetime.now()
        pass

    def getPacketId(self): # Get the id of the packet
        return self.id

    def getData(self): # Get the data of the packet
        return self.data
    
    def getChannel(self): # Get the stream at which the packet has been sent to
        return self.channelType
    
    def getTimeStamp(self): # Get the time stamp at which the packet was created
        return self.timeStamp
    
    def convertToBytes(self): # Convert to bytes to be suitable for sending across aioquic
        header = struct.pack('!B I Q', self.isRel)


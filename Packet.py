import datetime
import itertools

class Packet:

    id_object = itertools.count()
    
    def __init__(self, data, isReliable):
        self.id = next(Packet.id_object)
        self.data = data
        self.isReliable = isReliable
        self.timeStamp = datetime.datetime.now()
        pass

    def getPacketId(self): # Get the id of the packet
        return self.id

    def getData(self): # Get the data of the packet
        return self.data
    
    def getReliability(self): # Get the reliability status of the packet
        return self.isReliable
    
    def getTimeStamp(self): # Get the time stamp at which the packet was created
        return self.timeStamp


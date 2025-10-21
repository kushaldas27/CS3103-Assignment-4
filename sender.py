import random
from packet import Packet

def main():

    for i in range(10):
        
        isReliable = random.randint(0,1) # Randomizer to determine between 0 (Unreliable) and 1 (Reliable)
        data = "fwfwef" # Hardcoded data

        # TODO
        # packet construction shd be sent to gameNetAPI

        packet = Packet(data, isReliable) 

        print(f"---------Packet {i}-----------")
        print("Packet ID :", packet.getPacketId())
        print("Created at :", packet.getTimeStamp())
        print("Assigned Channel :", packet.getChannel())
        print("Contained Data :", packet.getData())
        print("Bytes format :")
        
    return



if __name__ == "__main__":
    main()
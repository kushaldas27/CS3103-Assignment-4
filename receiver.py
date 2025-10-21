import random
from packet import Packet

def main():

    for i in range(10):
        
        isReliable = random.randint(0,1) # Randomizer to determine between 0 (Unreliable) and 1 (Reliable)
        data = "fwfwef" # Hardcoded data

        packet = Packet(data, isReliable)

        print("P")


    return



if __name__ == "__main__":
    main()
class LaneConnector:
    """
    Represents the conection to the bowling lane

    Attributes
    ----------
    input_size: int
        represents the bit size that is used. default 16

    Methods
    -------
    getInput -> int
    """

    def __init__(self, input_size=16):
        self.input_size = input_size
        self.max_num = 2 ** self.input_size

    def getInput(self):
        """
        getInput obtains then returns a valid 16 bit integer input from stdin

        :return: a 16 bit integer
        """

        while 1:
            try:
                inpt = int(input())

                if inpt > self.max_num or inpt < 0:
                    print(f"{inpt}: invalid input")
                    continue

                return inpt

            except ValueError:
                print(f"invalid input")


"""
16 bit int format


      000000   0000000000
    |metadata| |--pins--|

    meta: 16 15 14 13 12 11

        16- nothing
        15- nothing
        14- nothing
        13- turn off the lane
        12- reset frame
        11- second throw


    pins: 10 9 8 7 6 5 4 3 2 1

        10 9 8 7
          6 5 4
           3 2
            1


    Valid Throw 1 range: 0-1023
    Valid Throw 2 range: 1024-2047

    Example->
           meta      pins
          xxx1xx xxxxxxxxxx -> turn off
          xxx01x xxxxxxxxxx -> reset the current frame

          xxx000 1111111111 -> strike

          xxx000 xxxxxxxxxx -> first throw
          xxx001 1111111111 -> second throw spare


          xxx000 0000000001 -> throw 1 knocks down pin 1
          xxx000 0000000011 -> throw 2 knocks down ONLY pin 2. 
                               Pin 1 is also reported due to limitations of machinery
                               This results in a score of 2

"""

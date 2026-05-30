from serial import Serial

# Bit computation
def LowByte(number : int):
    return number & 0xFF
def HighByte(number : int):
    return number >> 24 & 0xFF

# Data comunication
class DataPackage():
    def __init__(self, address, command, *args):
        self.address = address
        self.command = command
        self.args = args

    def Sent(self, port : Serial, return_bytes : int = 0):
        package = [self.address, self.command, *self.args]
        for data in package:
            port.write((data & 0xFF).to_bytes(1, byteorder="big"))
        if return_bytes > 0:
            return port.read(return_bytes)
        return None
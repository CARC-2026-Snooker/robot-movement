from serial import Serial

# Bit computation
def LowByte(number : int):
    return number & 0xFF
def HighByte(number : int):
    return number >> 24 & 0xFF

def UnsignedToSigned(number : int, width : int):
    return number if number < (1 << (width - 1)) else number - (1 << width)


# Data comunication
class DataPackage():
    def __init__(self, address, command, *args):
        self.address = address
        self.command = command
        self.args = args

    def Sent(self, port : Serial, byte_per_argument : int = 1, return_bytes : int = 0):
        package = [self.address, self.command]
        for arg in self.args:

            reverse_list = []
            for i in range(byte_per_argument):
                reverse_list.append((arg >> (8 * i)) & 0xFF)
            reverse_list.reverse()
            package.extend(reverse_list)

        for data in package:
            port.write(data.to_bytes(1, byteorder="big"))
        if return_bytes > 0:
            return port.read(return_bytes)
        return None
    
if __name__ == "__main__":
    print(UnsignedToSigned(0, 32))
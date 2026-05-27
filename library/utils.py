def LowByte(number : int):
    return number & 0xFF
def HighByte(number : int):
    return number >> 24 & 0xFF

# Illegal value checking
def ChannelCheck(channel : int):
    if channel != 1 and channel != 2:
        raise Exception("Channel out of range.")
def PowerCheck(power : int):
    if (power > 100 or power < -100) and power != 125:
        raise Exception("Power out of range.")
def SpeedCheck(speed : int):
    if speed > 720 or speed < -720:
        raise Exception("Speed out of range.")
def AbsSpeedCheck(degree : int):
    if degree > 720 or degree < 0:
        raise Exception("Speed out of range.")
    
def InvertCheck(invert : int):
    if invert != 1 and invert != 0:
        raise Exception("Invalid invert value.")
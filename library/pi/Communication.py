import spidev

class Communication:
    def __init__(self, speed : int = 1000000):
        self.spi = spidev.SpiDev()
        self.spi.max_speed_hz = speed

    def cleanUp(self):
        self.spi.close()
import cv2

class ImageProcessing:
    def __init__(self, frontCamera, rearCamera):
        self.frontCapture = cv2.VideoCapture(frontCamera)
        self.rearCapture = cv2.VideoCapture(rearCamera)

    def cleanUp(self):
        pass
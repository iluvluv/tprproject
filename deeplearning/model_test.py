#in rasberrypi
from TPRmodel import Model
import cv2
import numpy as np
cap = cv2.VideoCapture(0)
M = Model()

try:
    while(cap.isOpened()):
        ret, img = cap.read()
        output = M.result(img)
        print(np.argmax(output))    

except KeyboardInterrupt:
    cap.release()
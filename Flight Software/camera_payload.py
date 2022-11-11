from datetime import datetime
from pathlib import Path

import cv2 as cv2
import numpy as np


def __get_image():
    cam = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    result, image = cam.read() #result is unused at the moment, use it later for confirming whether the image is taken
    time = str(datetime.now())
    image = cv2.resize(image, (1440, 960))
    return (image, time)

def __proc_grayscale(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR) #Convert back to BGR to put colored text later
    return gray

def __proc_distort(image):
    #sk_gray, sk_color = cv2.pencilSketch(image, sigma_s=60, sigma_r=0.07, shade_factor=0.01) #Filter 1: Pencil Sketch
    #return sk_color
    #inv = cv2.bitwise_not(img) #Filter 2: Inverted Color
    #return inv
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) #Filter 3: Edge Detection
    #blur = cv2.GaussianBlur(gray, (3,3), 0) #blur image for better edge detection
    sobel = cv2.Sobel(gray, cv2.CV_32F, 1, 1, 1)
    sobel = (cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)*255).astype(np.uint8) #"casting" the sobel image (CV_32F) into the right format to blend with original image (uint 8)
    blended = cv2.addWeighted(image,0.5,sobel,0.5,0.0) 
    return blended

### Takes a picture
def take_picture(grayscale: bool, distort: bool, name: str):
    image, time = __get_image()
    if grayscale:
        image = __proc_grayscale(image)
    if distort:
        image = __proc_distort(image)
    cv2.putText(image, time,(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(image, time,(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA) 
    p = Path('.')/f'{name}.jpg' #Accessing current directory and giving the file a custom name
    cv2.imwrite(str(p),image)
    return str(p)

if __name__ == "__main__":
    print(take_picture(True, True, "GrayscaleDistort"))

import cv2
from datetime import datetime

cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)
result, image = cam.read()
time = str(datetime.now())

if result:
    gray = 255 - cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)*255
    blur = cv2.GaussianBlur(gray, (3,3), 0)
    sobel = cv2.Sobel(src=blur, ddepth=cv2.CV_32F, dx=1, dy=1, ksize=1)
    image = cv2.resize(image, (1440, 960))
    gray = cv2.resize(gray, (1440, 960))
    sobel = cv2.resize(sobel, (1440, 960))
    gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    sobel = cv2.cvtColor(sobel, cv2.COLOR_GRAY2BGR)
    cv2.putText(image, time,(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(image, time,(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(gray, time,(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(gray, time,(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.putText(sobel, time,(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
    cv2.putText(sobel, time,(20, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 1, cv2.LINE_AA)
    cv2.imshow('Original image',image)
    cv2.imshow('Gray image', gray)
    cv2.imshow('Sobil filtered image', sobel)
  
cv2.waitKey(0)
cv2.destroyAllWindows()

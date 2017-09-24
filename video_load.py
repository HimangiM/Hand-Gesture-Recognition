import numpy as np
import cv2

cap = cv2.VideoCapture(0)   #0 or -1

# print cap.isOpened()  #True

while True:
	
	ret, image = cap.read()   
	
	cv2.imshow('video', image)
	
	k = cv2.waitKey(10) & 0xff
	if k == 27:
		break

cap.release()
cv2.destroyAllWindows()

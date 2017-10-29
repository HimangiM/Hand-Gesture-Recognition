import numpy as np
import cv2

cap = cv2.VideoCapture(0)   #0 or -1

# print cap.isOpened()  #True

while True:
	
	ret, image = cap.read()   

	cv2.rectangle(image, (0, 0), (400, 400), (0, 255, 0), 1)   #image, first upper corner, second lower corner, color, thickness
	crop_img = image[0:400, 0:400]

	#Convert to grayscale, for better accuracy
	gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

	#Blur the Image
	blur = cv2.GaussianBlur(gray, (5, 5), 0)

	#thresholding the image
	ret, thresh1 = cv2.threshold(blur, 70, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU) #60 = threshold (vary it), 255 white color

	#display the threshold image
	cv2.imshow('Threshold', thresh1)

	#contour requires black and white object. The object to be found should be white
	contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

	
	#find hand using the maximum area in the rectangle
	maxArea = cv2.contourArea(contours[0])
	ci = 0
	for i in range(1,len(contours)):
		cnt = contours[i]
		area = cv2.contourArea(cnt)
		if(area>maxArea):
			maxArea = area
			ci = i
		cnt = contours[ci]
		
	#BGR -> (0,0,0)
	#draw the contour and convex full aroung hand
	cv2.drawContours(image, [cnt], 0, (0, 255, 0), 1)
	hull2 = cv2.convexHull(cnt)
	# cv2.drawContours(image, [hull2], 0, (255, 0, 0), 3)

	#find the convex hull
	hull = cv2.convexHull(cnt, returnPoints = False)
	defects = cv2.convexityDefects(cnt, hull)
	print len(defects)
	for i in range(defects.shape[0]):
	    s,e,f,d = defects[i,0]
	    start = tuple(cnt[s][0])
	    end = tuple(cnt[e][0])
	    far = tuple(cnt[f][0])
	    cv2.line(image,start,end,[255,0,0],2)
	    cv2.circle(image,far,5,[0,0,255],2)
	
	#finding convexity defects
	# for cnt in contours:
	# 	if (len(hull)>=3):
	# 		print 'f'
	# min_defect = 0
	# max_defect = 0
	# i = 0
	# for i in range(defects.shape[0]):
	# 	s,e,f,d = defects[i, 0]
	# 	start = tuple(cnt[s][0])
	# 	end = tuple(cnt[e][0])
	# 	far = tuple(cnt[f][0])
	# 	dist = cv2.pointPolygonTest(cnt, centr, True)
	# 	cv2.line(image, start, end, [0,0,255], 1)
	# 	cv2.circle(image, far, 5, [0, 0, 255], -1)
	# 	print(i)



	cv2.imshow('video', image)
	
	k = cv2.waitKey(10) & 0xff
	if k == 27:
		break

cap.release()
cv2.destroyAllWindows()

import cv2
import numpy as np

bg = None

#Running average
def run_avg(image, aWeight):
	global bg
	#If background None
	if bg is None:
		#Copy the current image as background
		bg = image.copy().astype("float")
		return 

	#Average the background frames
	cv2.accumulateWeighted(image, bg, aWeight)

def segment(image, threshold=25):
	global bg
	#Difference between background and current image
	diff = cv2.absdiff(bg.astype("uint8"), image)
	#Thresholding on the image, (black and white), white is the hand, black is the background
	_, thresholded = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU) 
	#Find all contours on thresholded image
	contours, hierarchy = cv2.findContours(thresholded.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

	if len(contours) == 0:
		return
	else:
		# segmented = max(contours, key = cv2.contourArea)
		#find contour with the max area i.e Hand
		maxArea = cv2.contourArea(contours[0])
		ci = 0
		for i in range(1,len(contours)):
			area = cv2.contourArea(contours[i])
			if(area>maxArea):
				maxArea = area
				ci = i
		return (thresholded, contours[ci])


if __name__=='__main__':
	passwords = []
	aWeight = 0.1
	camera = cv2.VideoCapture(0)
	top, right, bottom, left = 0, 0 ,400, 400
	num_frames = 0
	cur_frame = 0
	r = True
	l = []
	text = ""

	while True:
		#Read from camera
		(grabbed, frame) = camera.read()
		#Flip the image to avoid lateral inversion
		frame = cv2.flip(frame, 1)
		cv2.circle(frame, (200, 300), 1, (0,255,0), 3)
		clone = frame.copy()

		cv2.rectangle(clone, (top, right), (bottom, left), (0, 255, 0), 1)
		#Crop image
		crop_img = frame[top:bottom, right:left]
		#Convert cropped image to gray
		gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)
		#Blur the cropped image
		gray = cv2.GaussianBlur(gray, (7,7), 0)


		#running average on 30 frames
		k1 = cv2.waitKey(10) & 0xff

		font = cv2.FONT_HERSHEY_SIMPLEX

		present_frame = num_frames
		command_s = "s : Averaging"
		command_n = "n : New Password"
		command_e = "e : Enter Digit"
		command_c = "c : Confirm"
		command_esc = "esc : Exit"
		cv2.putText(clone, command_s,(420,20), font, 0.6, (255,255,255),2)
		cv2.putText(clone, command_n,(420,40), font, 0.6, (255,255,255),2)
		cv2.putText(clone, command_e,(420,60), font, 0.6, (255,255,255),2)
		cv2.putText(clone, command_c,(420,80), font, 0.6, (255,255,255),2)
		cv2.putText(clone, command_esc,(420,100), font, 0.6, (255,255,255),2)


		# cur_frame = num_frames
		#s for averaging
		if k1 == 115:
			cur_frame = num_frames 
		
		if num_frames < 100 or num_frames < cur_frame + 100:
			cv2.putText(clone,'Averaging. Please Wait.',(10,470), font, 1, (255,255,255),2)
			run_avg(gray, aWeight)
		else:
			digit = ""
			# segment the hand region
			#Register
			hand = segment(gray)

			if hand is not None:

				(thresholded, segmented) = hand

				#Draw the contour of hand, segmented contains the contour of hand
				cv2.drawContours(clone, [segmented], -1, (0, 255, 0))
				cv2.imshow("Theshold", thresholded)

				# find the convex hull, line
				hull = cv2.convexHull(segmented, returnPoints = False)

				#Points
				defects = cv2.convexityDefects(segmented, hull)

				for i in range(defects.shape[0]):
					s,e,f,d = defects[i,0]
					start = tuple(segmented[s][0])
					end = tuple(segmented[e][0])
					far = tuple(segmented[f][0])
					cv2.line(clone,start,end,[255,0,0],2)
					cv2.circle(clone,far, 5,[0,0,255],2)
					

				area = cv2.contourArea(segmented)
				length = cv2.arcLength(segmented, True)
				# print area
				
				approx = cv2.approxPolyDP(segmented, 0.1*cv2.arcLength(segmented, True), True)

				if area < 21000:
					digit = "ONE"
					cv2.putText(clone, digit,(10,470), font, 1,(255,255,255),2)

				if area > 21000 and area < 23000:
					digit = "TWO"
					cv2.putText(clone, digit,(10,470), font, 1,(255,255,255),2)

				if area > 23000 and area < 27000:
					digit = "THREE"
					cv2.putText(clone, digit,(10,470), font, 1,(255,255,255),2)

				if area > 27000 and area < 30000:
					digit = "FOUR"
					cv2.putText(clone, digit,(10,470), font, 1,(255,255,255),2)

				elif area > 30000:
					digit = "FIVE"
					cv2.putText(clone, digit,(10,470), font, 1,(255,255,255),2)

			if (r == True):
				# Register
				text = ""
				cv2.putText(clone,'Enter new password',(300,470), font, 1,(255,255,255),2)     
				
				k3 = cv2.waitKey(10) & 0xff

				#e = enter
				if k3 == 101:
					l.append(digit)
					print 'Entered', digit

				# c : confirm
				k2 = cv2.waitKey(10) & 0xff
				if k2 == 99:
					print l
					if l != []:
						passwords.append(l)
					l = []
					r = False
				
			elif (r == False):
				cv2.putText(clone,'Enter password to Login',(250,470), font, 1,(255,255,255),2) 

				k3 = cv2.waitKey(10) & 0xff

				#e = enter
				if k3 == 101:
					l.append(digit)
					print 'Entered', digit

				flag = 0
				k2 = cv2.waitKey(10) & 0xff
				#c to confirm
				if k2 == 99:
					if l in passwords:
						flag = 1
						print 'Login Successful.'
						text = 'Login Successful.'

					if flag == 0:
						print 'Login failed. Try Again.'
						text = 'Login failed. Try Again.'
						l = []
				
				cv2.putText(clone, text,(10,440), font, 0.7,(255,255,255),2)

				# n = new password 
				if k2 == 110:
					r = True  
					l = []  




		# increment the number of frames
		num_frames += 1

		cv2.imshow("Hand detection", clone)
		
		#esc to end program
		k = cv2.waitKey(10) & 0xff
		if k == 27:
			break

	camera.release()
	cv2.destroyAllWindows()

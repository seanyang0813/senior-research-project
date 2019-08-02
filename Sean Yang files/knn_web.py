import sys
import os
import dlib
import glob
import numpy as np
import timeit
import cv2
import time
import keyboard
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier

def distance(p1,p2):
	global normalize
	
	return np.array([p1.x-p2.x,p1.y-p2.y]) 
def distance2(p1,p2):
	return (p1.x-p2.x,p1.y-p2.y)
#cap = cv2.VideoCapture(0)
def initialize():
	global cap
	global prev
	global continues
	global predictor
	global predictor_path
	global detector
	global neigh
	global win
	global prev_gesture
	global gesture_count	
	predictor_path = os.getcwd()+"/68point.dat"
	win = dlib.image_window()
	detector = dlib.get_frontal_face_detector()
	#cnn_face_detector= dlib.cnn_face_detection_model_v1(os.getcwd()+"/mmod.dat")
	predictor = dlib.shape_predictor(predictor_path)
	xlist=list()
	ylist=list()
	dictionary=dict()
	prev_gesture=None
	gesture_count=0
	count=0
	tempmat=list()
	for i in os.listdir(os.getcwd()+"/gestures2"):	
		print(i)
		count+=1
		for j in os.listdir(os.getcwd()+"/gestures2/"+str(i)):
			#print(os.getcwd()+"/gestures/"+str(x)+"/"+str(y))
			#tries+=1
			#ret, img = cap.read()
			
			print(os.getcwd()+"/gestures2/"+str(i)+"/"+str(j))
			img = dlib.load_grayscale_image(os.getcwd()+"/gestures2/"+i+"/"+str(j))	
			faces = [dlib.rectangle(0, 0, img.shape[1],img.shape[0])]
			win.set_image(img)
			
			
			#print("Number of faces detected: {}".format(len(dets)))
			win.clear_overlay()
			for d in faces:
				forpca=list()
				
				#d = dlib.rectangle(d.left(), d.top(), d.right(), int(d.bottom()))
				#print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
				# Get the landmarks/parts for the face in box d.
				
				shape = predictor(img, d)  # this is mmod rectangle so we need .rect
				
				#print("Part 0: {}, Part 1: {} ...".format(shape.part(0), shape.part(1)))
				comp=shape.part(29)

				
				temp=distance(shape.part(27),shape.part(30))
				normalize=(temp[0]**2+temp[1]**2)**0.5
				for x in range(0,47,4):
					if x==0:
						dis=distance2(shape.part(x),comp)
						forpca.append(dis[0]/normalize)
						forpca.append(dis[1]/normalize)
					else:
						dis=distance2(shape.part(x),comp)
						forpca.append(dis[0]/normalize)
						forpca.append(dis[1]/normalize)
						# Draw the face landmarks on the screen.
				
				
				
				for x in range(47,68):
					#if x==47:
					#	forpca=distance(shape.part(x),comp)
					dis=distance2(shape.part(x),comp)
					forpca.append(dis[0]*5/normalize)
					forpca.append(dis[1]*5/normalize)

				
				win.add_overlay(shape)
				#t1=timeit.timeit()
			
				if count not in dictionary:
					dictionary[count]=[forpca]
				else:
					dictionary[count].append(forpca)
				print(forpca)
				xlist.append(forpca)
				ylist.append(i)
				
				
				#print(pca.explained_variance_ratio_)  
	#print(dictionary)
	for x in dictionary:
		print(dictionary[x])
		print('\nfor gesture '+str(x)+ "the average covariance are")
		print('x component:')
		print(sum([y[0] for y in dictionary[x]])/len(dictionary[x]))
		print('y component:')
		print(sum([y[1] for y in dictionary[x]])/len(dictionary[x]))
	neigh = KNeighborsClassifier(n_neighbors=7)
	neigh.fit(xlist, ylist)
	cap = cv2.VideoCapture(0)
	prev=None
	continues=0

def detect_gesture():
	global cap
	global prev
	global continues
	global predictor
	global predictor_path
	global detector
	global neigh
	global win
	global prev_gesture
	global gesture_count
	#while(True):
	#tries+=1

	ret, img = cap.read()
	#img = cv2.resize(img, dsize=(int(img.shape[1]),int(img.shape[0])), interpolation=cv2.INTER_CUBIC)
	img= cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
	win.set_image(img)
	dets = detector(img, 1)
		
		#print("Number of faces detected: {}".format(len(dets)))
	win.clear_overlay()
	for k, d in enumerate(dets):
		forpca=list()
		#print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(k, d.left(), d.top(), d.right(), d.bottom()))
		# Get the landmarks/parts for the face in box d.
		
		shape = predictor(img, d)
		
		win.add_overlay(shape)
		
		#print("Part 0: {}, Part 1: {} ...".format(shape.part(0), shape.part(1)))
		comp=shape.part(29)
		temp=distance(shape.part(27),shape.part(30))
		normalize=(temp[0]**2+temp[1]**2)**0.5
		for x in range(0,47,4):
			if x==0:
				dis=distance2(shape.part(x),comp)
				forpca.append(dis[0]/normalize)
				forpca.append(dis[1]/normalize)
			else:
				dis=distance2(shape.part(x),comp)
				forpca.append(dis[0]/normalize)
				forpca.append(dis[1]/normalize)
				# Draw the face landmarks on the screen.
		
		
		
		for x in range(47,68):
			#if x==47:
			#	forpca=distance(shape.part(x),comp)
			dis=distance2(shape.part(x),comp)
			forpca.append(dis[0]*5/normalize)
			forpca.append(dis[1]*5/normalize)
			
		#win.add_overlay(shape)
		#t1=timeit.timeit()
		
		
		#print(neigh.predict(np.asarray(forpca).reshape(1,-1)))
	
		

		
		cur_gesture=str(neigh.predict(np.asarray(forpca).reshape(1,-1))[0])
		if cur_gesture!=prev_gesture:
			prev_gesture=cur_gesture
			gesture_count=0
		else:
			gesture_count+=1
			if gesture_count==3:
				print(prev_gesture)
				print('pressed')
				if prev_gesture=='left':
					keyboard.press('up')
				if prev_gesture=='right':
					keyboard.press('down')
		print(cur_gesture)
		

initialize()
while True:
	detect_gesture()
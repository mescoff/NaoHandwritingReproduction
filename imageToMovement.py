# -*- encoding: UTF-8 -*-

import almath
import motion
import argparse
import time
import sys
import sensorsTouch
import takePicLetter
import getContours
import pickle
import os
import copy
import matplotlib.pyplot as plt

from naoqi import ALProxy
from naoqi import ALProxy
from naoqi import ALBroker

currentTestNumber= 0	#method AnalyzeLetter()
currentPath=""		#method AnalyzeLetter()

#Notes for myself: Hands are actuators, Other chains are effectors

handPositionWhenCrouching = [0.18149471282958984, -0.04990927875041962, 0.28647539019584656, 1.2931467294692993, -0.1829196810722351, 0.5396256446838379]
handPositionWhenStanding = [0.197179913520813, -0.06625422090291977, 0.33624497056007385, 1.6540746688842773, 0.04932650178670883, 0.24361510574817657]
handPositionToUse = [0.152452751994133, -0.11877129971981049, 0.449939101934433, 1.4863226413726807, -0.2542329728603363, 0.6075512170791626]

#get coordinates of /angle of an effector
def getEffectorPosition(motionProxy,currentPath):
	effectorList = ["RArm","RWristYaw","RShoulderPitch","RShoulderRoll","RElbowYaw","RElbowRoll","HeadPitch","HeadYaw"]
	#Set stiffness to 0 to move manually arm to wanted position
	
	'''print("get ready to put head in desired position")
	time.sleep(4)
	motionProxy.setStiffnesses(effectorList[6], 0.0)
	angle = motionProxy.getAngles(effectorList[6],False) 
	print("head pitch:",str(angle))
	angle = motionProxy.getAngles(effectorList[7],False) 
	print("head yaw:",str(angle))'''
	
	motionProxy.setStiffnesses(effectorList[0], 0.0)
	
	print("chose movement now. You have 5 seconds")
	time.sleep(5) #wait for manual movement to be set by user
			
	#Position the Arm	
	frame = motion.FRAME_ROBOT
	useSensorValues = False
	f=open(os.path.join(currentPath,"armOriginPosition.txt"),"w")
	
	#get arm position
	currentPos = motionProxy.getPosition(effectorList[0], frame, useSensorValues)
	print("currentPos RArm: " + str(currentPos))
	f.write("currentPos RArm: " + str(currentPos)+"\n")
	
	#get wrist angle
	angle = motionProxy.getAngles(effectorList[1],True)   #secondArgument = activateSensors
	f.write("wrist angle: " + str(angle)+"\n")
	angle = motionProxy.getAngles(effectorList[2],True)   #secondArgument = activateSensors
	f.write("RShoulderPitch angle: " + str(angle)+"\n")
	angle = motionProxy.getAngles(effectorList[3],True)   #secondArgument = activateSensors
	f.write("RShoulderRoll angle: " + str(angle)+"\n")
	angle = motionProxy.getAngles(effectorList[4],True)   #secondArgument = activateSensors
	f.write("RElbowYaw angle: " + str(angle)+"\n")
	angle = motionProxy.getAngles(effectorList[5],True)   #secondArgument = activateSensors
	f.write("RElbowRoll angle: " + str(angle)+"\n")
	f.close()
	

#record manually several positions of the arm 
def recordWriting(motionProxy,currentPath):
	print("Recording Writing")
	effector = "RArm"
	#Set stiffness to 0 to move manually arm to wanted position
	motionProxy.setStiffnesses(effector, 0.0)
	frame = motion.FRAME_ROBOT
	useSensorValues = False
	movementsList = []
	
	#time.sleep(4)
	#position arm in different required positions to achieve final movement
	for i in range (10):
		print("Position"+str(i)+": chose movement now. You have 10 seconds")
		time.sleep(1) #wait for manual movement to be set by user
		currentPos = motionProxy.getPosition(effector, frame, useSensorValues)
		print("Position1 coordinates: "+str(currentPos))
		movementsList.append(currentPos)
	pickle.dump( movementsList, open( "recordedMovementsList.p", "wb" ) )
	print("Done recording")
	
	f = open(os.path.join(currentPath,"armPositions.txt"),"w")
	for i in movementsList:
		f.write(str(i)+"\n")
	f.close()

#bring arm to writing position	
def bringArmToPosition(motionProxy):
	#effectorList = ["RArm","RWristYaw","RHipRoll","LHipRoll"]
	'''frame = motion.FRAME_ROBOT
	useSensorValues = False
	times = [2.0]	

	positionsList = []    #in case we want several positions later
	axisMask = motion.AXIS_MASK_VEL
	
	#positionArm
	targetPos = handPositionToUse
	#positionsList.append(list(targetPos.toVector())) #no need to make targetPos into a Vector, it already is one
	#Also list is here just in case we want to add other movements
	positionsList.append(list(targetPos))'''
	
	motionProxy.setStiffnesses("RArm", 1.0)
	
	#positionWrist
	#angle = 0.3
	angle=1.5
	fractionMaxSpeed = 0.2
	motionProxy.setAngles("RWristYaw", angle, fractionMaxSpeed)
	
	#position Shoulder and Elbow
	angleShoulderPitch = -0.1779019832611084
	motionProxy.setAngles("RShoulderPitch", angleShoulderPitch, fractionMaxSpeed)
	
	#angleShoulderRoll = -0.9725980758666992
	angleShoulderRoll = -0.9
	motionProxy.setAngles("RShoulderRoll", angleShoulderRoll, fractionMaxSpeed)
	
	angleElbowRoll = 1.4818859100341797
	motionProxy.setAngles("RElbowRoll", angleElbowRoll, fractionMaxSpeed)

	angleElbowPitch = 0.04137611389160156
	motionProxy.setAngles("RElbowYaw", angleElbowPitch, fractionMaxSpeed)
	
	#motionProxy.positionInterpolations(effectorList[0], frame, positionsList,axisMask, times)
	
#reproduce pre-recorded movements
def reproduceMovementsOld(motionProxy,movementsList):
	#movementsList = pickle.load(open( "recordedMovementsList.p", "rb" ))
	#movementsList = pickle.load(open( "letterMovements.p", "rb" ))
	effectorList = ["RArm"]
	frame = motion.FRAME_ROBOT
	#axisMask = almath.AXIS_MASK_VEL
	axisMask = almath.AXIS_MASK_X + almath.AXIS_MASK_Y + almath.AXIS_MASK_Z
	useSensorValues = False
	times=[]
	#print ("currentPos:",str(currentPos))
	'''f = open("recordedMovementsLis.txt","w")
	for i in movementsList:
		f.write(str(i)+"\n")
	f.close()	'''
	
	#movementsList = scaleLetterPoints(currentPos)
	#print movementsList
	#add as many times as there is 6D positions/points in our list
	for i in range(len(movementsList)):
		times.append(i+0.5)			
	print times
		
	#PB: robot doesn't make movements, it does only one WHY
	# I also recorded the points needed to write a C manually and can compare with the list I get from contours
	#NOTHING IS WORKING SO i THINK I NEED TO ACTUALLY INCREMENT AND DECREMENT THE X AND Y OF THE CURRENT POSITION EVERY TIME. SO FROM
	# LIST OF POINTS LETTER i SHOULD CALCULATE BY HOW MUCH i NEED TO INCREASE OR DECREASE THE NEXT POSITION

	motionProxy.positionInterpolations(effectorList[0], frame, movementsList,axisMask, times)
	
	'''fractionMaxSpeed = 0.5
	for i in movementsList[0:10]:
		print("movement")
		motionProxy.setPositions(effectorList[0], frame, i, fractionMaxSpeed, axisMask)
	#time.sleep(1)'''
	


#use transform to write letter	
def reproduceMovement(motionProxy,movementsList):
	effectorList = ["RHand","Torso","RArm"]
	frame = motion.FRAME_ROBOT
	axisMask = almath.AXIS_MASK_X + almath.AXIS_MASK_Y + almath.AXIS_MASK_Z
	handPos = motionProxy.getPosition(effectorList[0],frame,False)
	torsoPos = motionProxy.getPosition(effectorList[1],frame,False)
	rightArm = motionProxy.getPosition(effectorList[2],frame,False)
	times=[]
	#movementsList=pickle.load(open( "finalMovementsList.p", "rb" ))
	#print(handPos)
	
	
	for i in range(len(movementsList)):
		times.append(i+1)			
	print times
	
	print ("movements list done")
	
	#TRIAL 1
	motionProxy.positionInterpolations(effectorList[2], frame, movementsList,axisMask, times)
	#WE STILL HAVE A PROBLEM, IT DOES RIGHT MOVEMENTS AT THE BEGINNING THEN STARTS MAKING WAKY MOVEMENTS. Is it because its going back to an anterior
	#position?
	
	#TRIAL 2: FROM POSITION 11 its getting weird. Why?
	#Should I just keep changing the handPos x and y? (increment or decrease them at each movement, so that rest of position6D is adapted and doesn't make weird things)
	'''fractionSpeed = 1
	for i in range(len(movementsList)):	
		print("setting position",str(i),":",str(movementsList[i]))
		motionProxy.setPositions(effectorList[2], frame, movementsList[i], fractionSpeed, axisMask)
		time.sleep(1)'''
		
	
	''' TEST 3. This works, no waky movement
	motionProxy.setPositions(effectorList[2], frame, movementsList[0],0.5 , axisMask)
	time.sleep(1)
	motionProxy.setPositions(effectorList[2], frame, movementsList[len(movementsList)/2], 0.5, axisMask)
	time.sleep(1)
	motionProxy.setPositions(effectorList[2], frame, movementsList[len(movementsList)-1], 0.5, axisMask)'''

	

def scaleLetterPoints(currentPath):
	arrayFile = os.path.join(currentPath,"letter.p")
	listOfPoints=[]
	
	# get pickled list of contours for C for example.
	# have a loop that for each point takes the x and y and adds them to a new 6D vector (should have z,dx,dy,dz positiono of arm when ready to write
	letterArray=pickle.load(open(arrayFile,"rb"))
	
	#pixels to meters and to Nao(x,-y) space
	for value in letterArray:
		point=[]
		#vector6D = copy.copy(currentPosition)
		#we reverse. The x and y from letter become the y and x of 6d vector + I make them smaller by mult by 0.3 to avoid reaching Nao's space limits and to make
		# him do smaller mvts 
		newX= (float(value[1])/1850)*0.4
		newY=(-(float(value[0])/1600)*0.4)
		point.insert(0,newX)  #scale y and put it into x slot of position6D
		point.insert(1,newY) #scale x
		listOfPoints.append(point)
		
	f = open(os.path.join(currentPath,"scaledLetterPositions.txt"),"w")
	for i in listOfPoints:
		f.write(str(i)+"\n")
	f.close()
	
	#TEST
	#for x,y in listOfPoints:
		#plt.scatter(x, y)
	#plt.show()

	#evolution of points from starting point (the difference between each point and the origin-> we will add it to point of origin of hand)
	evolList=[]
	for i in range(len(listOfPoints)):
		evolPoint=[]
		evolPoint.insert(0, (listOfPoints[i])[0] - (listOfPoints[0])[0] )
		evolPoint.insert(1,(listOfPoints[i])[1] - (listOfPoints[0])[1] )
		evolList.append(evolPoint)
			
	f = open(os.path.join(currentPath,"evolLetterPositions.txt"),"w")
	for i in evolList:
		f.write(str(i)+"\n")
	f.close()	
	
	print ("Evol list done")
	return evolList
	
def finalizeMovementsList(motionProxy,evolList,currentPath):	
	frame = motion.FRAME_ROBOT
	handPos = motionProxy.getPosition("RHand",frame,False)
	print("handPos:",str(handPos))
	movementsList=[]
	for i in evolList:
		newPos=copy.copy(handPos)
		newPos[0]=newPos[0]+(i[0])
		newPos[1]=newPos[1]+(i[1])
		movementsList.append(newPos)
	
	f = open(os.path.join(currentPath,"finalMovementsList.txt"),"w")
	for i in movementsList:
		f.write(str(i)+"\n")
	f.close()
	
	'''TEST, see if putting evol (x,y) values onto hand origin position worked
	for i in movementsList:
		plt.scatter(i[0], i[1])
	plt.show()'''
	
	print("final movement list done")
	pickle.dump(movementsList, open(os.path.join(currentPath,"finalMovementsList.p"), "wb" ) ) #Not used but just in case
	return movementsList
	
	
#Activates touch sensors to trigger the closing of the hand when hand sensor is pressed
def reactToTouch():
	global ReactToTouch
	ReactToTouch = sensorsTouch.ReactToTouch("ReactToTouch")
	ReactToTouch.loop()

def recordLetter():
	# take pic and process the picture
	global RecordLetter
	RecordLetter = takePicLetter.letterRecording()
	RecordLetter.takePic()

def analyzeLetter():
	global AnalyzeLetter
	AnalyzeLetter = getContours.letterAnalysis()
	AnalyzeLetter.run()
	currentTestNumber = AnalyzeLetter.getN()
	currentPath = AnalyzeLetter.getCurrentPath()
	
	list =[]
	list.append(currentTestNumber)
	list.append(currentPath)
	return list
	
	

def main(robotIP, PORT=9559):
	# We need this broker to be able to construct
	# NAOqi modules and subscribe to other modules
	# The broker must stay alive until the program exists
	myBroker = ALBroker("myBroker",
	   "0.0.0.0",   # listen to anyone
	   0,           # find a free port and use it
	   robotIP,          # parent broker IP
	   PORT)        # parent broker port

	#StartProxies
	motionProxy  = ALProxy("ALMotion")
	postureProxy = ALProxy("ALRobotPosture")
	tts = ALProxy("ALTextToSpeech")


	
	# Send robot to Pose Init
	postureProxy.goToPosture("StandInit", 0.5) #other postures exists - Stand/StandInit/StandZero/Crouch

	
	#Loop for the broker
	try:
		while True:
			time.sleep(1)
			
			recordLetter()
			
			
			list = analyzeLetter()
			currentTestNumber = list[0]   #get values from getContours
			currentPath = list[1]
			
			time.sleep(4)
			#getEffectorPosition(motionProxy,currentPath)
			
			#BringArmToPosition
			bringArmToPosition(motionProxy)
			time.sleep(1)
			
			#TEST - Get position of arm to set it
			#print("Checking position of torso")
			time.sleep(1)
			
			#generate the list of the "evolution" of the letter from the starting point. Then generate final list of mv from it.
			#WAS AFTER reactToTouch(), MOVED HERE
			evolList = scaleLetterPoints(currentPath)
			movementsList = finalizeMovementsList(motionProxy,evolList,currentPath)
			
			#OpenHand
			motionProxy.openHand("RHand")
			time.sleep(1)
			
			tts.say("Please give me the pen. Touch the sensor on my right hand when it's ready")
			
			#activate sensors, wait for touch to close hand and begin drawing	
			reactToTouch()
			
			
			reproduceMovement(motionProxy,movementsList)
			
			
			#print("hand is in positon. Be ready to catch the arm")
			time.sleep(2)
			#recordWriting(motionProxy,currentPath)
			
			tts.say("I am done. Can you take the pen back?")
			motionProxy.openHand("RHand")
			
			#generate file that contains current testNumber to keep track of number of tests
			print("Test number "+str(currentTestNumber)+" is over, creating a new testNumber and saving it")			
			currentTestNumber+=1 
			pickle.dump(currentTestNumber, open( "currentTestNumber.p", "wb" ) )
			print("Test number saved")
			
			tts.say("Get ready to turn me off")
			time.sleep(4)

	except KeyboardInterrupt:
		# Go to rest position
		motionProxy.rest()
		print "Interrupted by user, shutting down"
		myBroker.shutdown()
		sys.exit(0)	

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	#parser.add_argument("--ip", type=str, default="127.0.0.1",help="Robot ip address")
	parser.add_argument("--ip", type=str, default="10.10.46.180",help="Robot ip address")
	#parser.add_argument("--port", type=int, default=9759,help="Robot port number")   #TO USE WITH SIMULATOR
	parser.add_argument("--port", type=int, default=9559,help="Robot port number")

	args = parser.parse_args()
	main(args.ip, args.port)

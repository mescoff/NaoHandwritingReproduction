import numpy as np
import cv2
import matplotlib.pyplot as plt
import pickle
import os.path
from matplotlib import animation
from PIL import Image
from PIL import ImageEnhance

"""
INFO
cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE) ==  return Numpy arrays of (x,y)
cv2.drawContours(IMG, arrays, DRAWINGMODE, COLOR, THICKNESS)
"""

class letterAnalysis():
	
	def __init__(self):
		self.image = 'letterImage.png'
		
		#Make directories for data at every new test
		self.testNFile = "currentTestNumber.p"
		if not os.path.exists(self.testNFile):
			self.n = 1
			self.folderName = "test"+str(self.n)
			self.path= os.path.join("C:\Users\Manon\Desktop\Fall 2014\Nao\FinalWriting",self.folderName)
			os.makedirs(self.path)
		else:			
			self.n=pickle.load(open(self.testNFile,"rb"))
			self.folderName = "test"+str(self.n)
			self.path= os.path.join("C:\Users\Manon\Desktop\Fall 2014\Nao\FinalWriting",self.folderName)
			os.makedirs(self.path)
		
		

	#crop image to focus on letter
	def cropImage(self):
		im = Image.open(self.image)
		imArray = im.load()
		width,height = im.size
		reducX = 80
		reducY = 55
		box = (reducX,reducY, width-reducX,height-reducY)   #box(left,upper,right,lower)
		im = im.crop(box)
		im.save(os.path.join(self.path,'text'+str(self.n)+'.png'))
		return im
		'''newImg = Image.new('RGB', (width-10,height-10))
		newArray = newImg.load()
		for y in range(10,height):
			for x in range(10,width):
				newArray[x-10,y-10] = (imArray[x,y])
				#print(imArray[x,y])
				#print(newArray[x,y])
		#img= Image.fromarray(newArray)'''

	#increase saturation of pixels. Returns a numpy array	
	# NOT USED FOR NOW because loosing data rather than gaining some
	def histoEqual(self,inputImg):     
		imgArray = np.array(inputImg) 
		#convert letter to BW so clahe can be applied to it
		imgray = cv2.cvtColor(imgArray,cv2.COLOR_BGR2GRAY) 
		# create a CLAHE object (Arguments are optional).
		clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
		cl1 = clahe.apply(imgray)

		clahename = 'equalized'+str(self.n)+'.png'
		cv2.imwrite(os.path.join(self.path,cahename),cl1)
		return cl1

	#Inhance the saturation of picture to increase darkness of black pixels
	# NOT USE EITHER. Barely increases the saturation of the back pixels
	def enhanceColor(self,inputImg):
		converter = ImageEnhance.Color(inputImg)
		img2 = converter.enhance(2)
		newname = 'inhanced'+str(self.n)+'.png'
		img2.save(newname)
		return img2

	#Isolate the dark pixels in image to isolate the letter
	#Takes an Image, returns a numpy array
	def isolateDarkPix(self,inputImg):			
		imgArray = np.array(inputImg) 						#turn PIL image into numpy array for opencv functions
		#iterate through numpy array of img. If img.pixel value is greater than 50 (so if it's anything else than pure black), change it to 255 (white)
		imgArray[imgArray > 60] = 255	
		newname = 'isolated'+str(self.n)+'.png'
		cv2.imwrite(os.path.join(self.path,newname),imgArray)
		return imgArray


	def contoursOfImage(self,inputArray):
		imgray = cv2.cvtColor(inputArray,cv2.COLOR_BGR2GRAY)     
		ret,thresh = cv2.threshold(imgray,127,255,cv2.THRESH_BINARY_INV)   #apply threshold, use binary inverse to focus on black part rather than white part. RETURN AN IMG
		contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE) #gets only important corners (in case straight lines). Consumes less space
		#contours, hierarchy = cv2.findContours(thresh,cv2.RETR_TREE,cv2.CHAIN_APPROX_NONE)  #gets all points. RETURN 

		cv2.drawContours(inputArray, contours, -1, (0,255,0), 3) #draw contours
		#cv2.drawContours(inputArray, contours, -1, (0,255,0), -1) #fill inside edges

		cv2.imwrite(os.path.join(self.path,'contours'+str(self.n)+'.png'),inputArray)
		#contours is a Python list of all the contours in the image. Each individual contour is a Numpy array of (x,y) coordinates of boundary points of the object.
		return contours


	#Test function to give me information about the contour Array
	def arrayInfo(self,list):
		#EACH ELEMENT IN LIST[N] IS A NUMPARY ARRAY OF X,Y POINTS
		
		f = open(os.path.join(self.path,"ArrayOfContours"+str(self.n)+".txt"),"w")
		i = 0
		for numpyArray in list:
			print("Contour"+str(i))
			f.write("Contour"+str(i)+"\n")
			#print type(numpyArray)
			print("shape of array: "+ str(numpyArray.shape))
			print("ndim of array: "+ str(numpyArray.ndim))
			print("size of array: "+ str(numpyArray.size))
			f.write("shape of array: "+ str(numpyArray.shape)+"\n" )
			f.write("ndim of array: "+ str(numpyArray.ndim)+"\n")
			f.write("size of array: "+ str(numpyArray.size)+"\n")
			#print("itemSize of array: "+ str(numpyArray.itemSize))
			print ("---------------")
			f.write("--------------- \n")
			i+=1

		
		#for numpyArray in list:	
		#for v, value in np.ndenumerate(list[4]):
			#print value
		
		f.close()

	#run through list of contours and return contour that contains the most points/data.
	#returns a numpy array
	def findRelevantContour(self,list):
		i = 0 #keep track of index in list
		maxValue,indexOfMax=0,0
		for numpyArray in list:
			if (numpyArray.shape[0]>maxValue):
				maxValue = numpyArray.shape[0]
				indexOfMax=i
			i+=1
		print("the Contour with the most points is contour: "+str(indexOfMax)+" with n.point: "+str(maxValue))
		return list[indexOfMax]
			

	#clusterize the points of contour into boxes to get reduce the actual contour into one single line	
	#Contour is a numpy array of (x,y)points (numpyArray as well)
	def clusterizeArray(self,contour):
		#holds the value of reference of each box to compare to value that needs to be placed in box.
		referencesPerBox = []
		listOfPoints = []
		listOfBoxes = []
		r = open(os.path.join(self.path,"1-clusterisationProcess.txt"),"w")
		x = open(os.path.join(self.path,"2-clusterisedArray.txt"),"w")

		#for x,y in (contoursList[4].flatten().reshape(-1,2)):
		#slicing array : array[start:stop:step]	
		#contoursList[4].flatten().reshape(-1,2))[0:300:1]    IN CASE WE WANT TO FRAGMENT THE LIST
		self.showPoints((contour.flatten().reshape(-1,2)))
		for value in ( (contour.flatten().reshape(-1,2)) ):
			#Base case: List of Boxes is empty
			#Creates the first box and puts the first point from our numpArray in it
			if (not listOfBoxes):
				listOfPoints.append(value)
				referencesPerBox.append(value)
				listOfBoxes.append(listOfPoints)
			
			
			#List of Boxes has more than one box
			elif (len(listOfBoxes)>0):		
				needNewBox = True
				#I'm using indexes here because it represents the number of the box
				for i in range(len(referencesPerBox)):
					#keep adding points that belong to box 0 into it. We use reference value of box for that: if the new value is greater or less than reference by 20, it belongs to a new box
					#create a new cluster everytime the diff between 2 points is bigger than 30 (the bigger the value, the less clusters)
					if ( (abs(value-referencesPerBox[i]) < 20).all() ):
						listOfBoxes[i].append(value)
						#print("value "+str(value)+" goes to box: "+str(i))
						r.write("value "+str(value)+" goes to box: "+str(i)+"\n")
						needNewBox = False
					
					else:
						#print ("value "+str(value)+"doesn't fit in box:"+str(i))
						r.write("value "+str(value)+"doesn't fit in box:"+str(i)+"\n")
				
				if needNewBox == True:
					#print("\nWe need a new box")
					r.write("We need a new box \n")
					#We came out of loop without finding a match so we create a new box. Then we get to next value (thanks to value loop), which will get access to new reference
					listOfPoints=[]
					listOfPoints.append(value)
					referencesPerBox.append(value) #new reference for box 1
					listOfBoxes.append(listOfPoints)
					#print ("length of Box list is NOW: "+ str(len(listOfBoxes)))
					r.write("length of Box list is NOW: "+ str(len(listOfBoxes))+"\n")
					#print("Reference list is now: "+str(len(referencesPerBox))+"\n")
					r.write("Reference list is now: "+str(len(referencesPerBox))+"\n")
					
		print("\n")
		#print(listOfBoxes)	
		for i in range (len(listOfBoxes)):
			x.write("Box "+str(i)+": "+str(listOfBoxes[i])+"\n")
		
		x.close()
		r.close()
		return listOfBoxes		
			
			
	def averagingClusters(self,list):
		# new list to hold average point for each box/cluster
		newClusterList = []
		for i in range(len(list)):
			print("averaging points at box:"+str(i))
			#reset var
			totalX,totalY,averageX,averageY=0,0,0,0
			for x,y in list[i]:
				totalX+=x
				totalY+=y
			averageX=totalX/len(list[i])
			averageY=totalY/len(list[i])
			print(averageX,averageY)
			#create a new numpy array to store the x,y points and add it a new list of boxes (at right index, as index is the number of the box)
			point = np.array([averageX,averageY])
			newClusterList.insert(i,point)
		
		#print(newClusterList)
		f = open(os.path.join(self.path,"3-averagedClusterisedArray.txt"),"w")
		for i in range (len(newClusterList)):
			f.write("Box "+str(i)+": "+str(newClusterList[i])+"\n")
		f.close()
		return newClusterList

	#mirror the points on the x axis to flip the letter in the correct position
	def mirrorPoints(self,list,imageWidth,imageHeight):
		mirroredArray = list #making a copy just in case
		for value in mirroredArray:
			newX = imageWidth-value[0]
			#newY = imageHeight-value[1]
			value[0]=newX
			#value[1]=newY
		
		f = open(os.path.join(self.path,"4-averagedArrayMirrored.txt"),"w")
		for value in mirroredArray:
			f.write(str(value)+"\n")
		f.close()
		
		#save array into a file that the robot can use
		pickle.dump(mirroredArray, open(os.path.join(self.path,"letter.p"), "wb" ) )

		return mirroredArray
		

	def showPoints(self,list):
		for x,y in list:
			plt.scatter(x, y)
		plt.show()

	def drawLetter(self,list):
		plt.axes()
		for i in range(len(list)):
			print(i)
			if(i!=(len(list)-1)):
				print("x are: ",str((list[i])[0])," ",str((list[i+1])[0])," y are: ", str((list[i])[1]), " ", str((list[i+1])[1]))
				print("drawing line between points ",str(list[i]), " ",str(list[i+1]))
				dotted_line = plt.Line2D(( (list[i])[0], (list[i+1])[0]), ((list[i])[0], (list[i+1])[1]), lw=5., 
								 ls='-.', marker='.', 
								 markersize=50, 
								 markerfacecolor='r', 
								 markeredgecolor='r', 
								 alpha=0.5)
				plt.gca().add_line(dotted_line)
				#plt.scatter(x, y)	
		plt.axis('scaled')
		plt.show()
		

	
	def getN(self):
		return self.n 
		
	def getCurrentPath(self):
		return self.path
		

	def run(self):	
		croppedImg = self.cropImage()				#image
		#enhanceImg = enhanceColor(croppedImg)   #image
		blackPixArray = self.isolateDarkPix(croppedImg)  #array
		cont = self.contoursOfImage(blackPixArray)		#contour is a list of numpyArrays(which contain (x,y) numparray)
		
		#Give us info about what the list of contours contains
		self.arrayInfo(cont)
		#Get the contour with the most points, to discard contours that are just noise in the picture
		relevantContour = self.findRelevantContour(cont)
		
		
		#Arrange the array into clusters to find the average points that constitute the letter (and trajectory)
		clusters = self.clusterizeArray(relevantContour)
		averagedClusters = self.averagingClusters(clusters)
		#drawLetter(averagedClusters)
		#reverse letter for robot
		imWidth, imHeight = croppedImg.size	
		mirroredClusters = self.mirrorPoints(averagedClusters,imWidth,imHeight)
		self.showPoints(mirroredClusters)
		#self.drawLetter(mirroredClusters)
		
		#generate file that contains current testNumber
		#self.n+=1 
		#pickle.dump(self.n, open( "currentTestNumber.p", "wb" ) )
	
	
	

	
	
	

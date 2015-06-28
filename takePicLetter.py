# -*- encoding: UTF-8 -*-
# Get an image from NAO. Display it and save it using PIL.
''' Get robot to look for a face while up, he says somght like "what am I going to draw today? click my head when you're ready to start"
click on head, it looks at the page and asks you to tap on head again when we're done. '''

import sys
import time
import argparse
# Python Image Library
import Image

from naoqi import ALProxy

class letterRecording():
	
	def __init__(self):
		#Module for ALTextToSpeech
		self.tts = ALProxy("ALTextToSpeech")
		self.motionProxy = ALProxy("ALMotion")
		self.camProxy = ALProxy("ALVideoDevice")
		
	
	def putHeadInPosition(self):
		effectorList = ["HeadPitch","HeadYaw"]
		headPitch = -0.0015759468078613281
		headYaw = 0.0
		fractionMaxSpeed = 0.2
		self.motionProxy.setAngles(effectorList[0], headPitch, fractionMaxSpeed)
		self.motionProxy.setAngles(effectorList[1], headYaw, fractionMaxSpeed)
		
		
	def takePic(self):
		"""
		First get an image from Nao, then show it on the screen with PIL.
		"""
		self.tts.say("Okay, you have 10 seconds to write the letter")
		time.sleep(10)
	
		self.tts.say("The letter is ready? Let me put my head in position")
		time.sleep(1)
		self.putHeadInPosition()
		self.tts.say("Okay, give me a second to take a picture")
		
		time.sleep(2)
		
		resolution = 2    # VGA
		colorSpace = 11   # RGB
		camIndex = 1    #0 is camera UP, 1 is camera DOWN
		fps = 5
		videoClient = self.camProxy.subscribeCamera("python_client", camIndex, resolution, colorSpace, fps)

		# Get a camera image.
		# image[6] contains the image data passed as an array of ASCII chars.
		naoImage = self.camProxy.getImageRemote(videoClient)

		# Now we work with the image returned and save it as a PNG  using ImageDraw
		# package.

		# Get the image size and pixel array. #[6]: binary array of size height * width * nblayers containing image data.
		imageWidth = naoImage[0]
		imageHeight = naoImage[1]
		array = naoImage[6]

		# Create a PIL Image from our pixel array.
		im = Image.fromstring("RGB", (imageWidth, imageHeight), array)

		# Save the image.
		imgName = "letterImage.png"
		im.save(imgName, "PNG")
		  
		self.camProxy.unsubscribe(videoClient)
		self.tts.say("I'm done. I hope the picture is good") #work on adding emotion in voice + sounds + movements reactions
		time.sleep(4)


	'''if __name__ == '__main__':
	  #IP = "nao.local"  # Replace here with your NaoQi's IP address.
	  #IP = "127.0.0.1"
	  IP = "10.10.29.201"
	  PORT = 9559

	  # Read IP address from first argument if any.
	  if len(sys.argv) > 1:
		IP = sys.argv[1]

	  takePicture('''



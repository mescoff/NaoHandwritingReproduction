# -*- encoding: UTF-8 -*-
""" Say `My {Body_part} is touched` when receiving a touch event
"""

import sys
import time

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule
import argparse

# Global variable to store the ReactToTouch module instance
ReactToTouch = None
memory = None


class ReactToTouch(ALModule):
	""" A simple module able to react
		to touch events.
	"""
	def __init__(self, name):
		ALModule.__init__(self, name)
		# No need for IP and port here because
		# we have our Python broker connected to NAOqi broker

		# Create a proxy to ALMotion for later use
		self.motionProxy = ALProxy("ALMotion")

		# Subscribe to TouchChanged event:
		global memory
		memory = ALProxy("ALMemory")
		memory.subscribeToEvent("TouchChanged","ReactToTouch","onTouched")
		
		self.boolean = True
		

	def loop(self):
		while self.boolean: 
			pass


	def onTouched(self, strVarName, value):
		""" This is called each time a touch
		is detected.	
		QUESTION HERE IS WHY DOES IT DETEC A TOUCH ON RIGHT HAND EVEN IF RIGHT HAND IS NOT BEING TOUCHED...
		WHICH IS WHY I HAD TO USE SPECIFICALLY "IF BACK OF RIGHT HAND IS TOUCHED...DO SMTHG"
		"""
		
		""" we could also do this without even using this whole class:
		for p in value:
			if (p[0] == "RHand/Touch/Back" AND p[1] == True):   do smthg"""

		print("touched activated")
		
		for p in value:
				print ("p[0] is "+p[0])
				if (p[0]=="RHand/Touch/Back"):
						# Unsubscribe to the event when talking,
						# to avoid repetitions
						memory.unsubscribeToEvent("TouchChanged","ReactToTouch")
						#close hand
						self.motionProxy.closeHand("RHand")
						self.boolean = False


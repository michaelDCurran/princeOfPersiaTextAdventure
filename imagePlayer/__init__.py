import os
import sys
import time
import math

sys.path.append(os.path.join(os.path.dirname(__file__), 'deps'))

import libaudioverse

class ImagePlayer:

	def __init__(self, lowFreq=220, highFreq=8192, width=176, height=64, reverseBrightness=False):
		self._lowFreq = lowFreq
		self._highFreq = highFreq
		self._width = width
		self._height = height
		self._reverseBrightness = reverseBrightness
		self._initWaves()

	def _initWaves(self):
		self._octiveCount=math.log(self._highFreq / self._lowFreq, 2)
		libaudioverse.initialize()
		self._lavServer=libaudioverse.Server()
		self._lavPanner=libaudioverse.MultipannerNode(self._lavServer,"default")
		self._lavPanner.strategy=libaudioverse.PanningStrategies.stereo
		self._lavPanner.should_crossfade=False
		self._lavPanner.connect(0,self._lavServer)
		self._lavWaves=[]
		for x in range(self._height):
			lavWave=libaudioverse.SineNode(self._lavServer)
			lavWave.mul=0
			lavWave.frequency.value=self._lowFreq*((2**self._octiveCount)**(x/self._height))
			lavWave.connect(0,self._lavPanner,0)
			self._lavWaves.append(lavWave)
		self._lavServer.set_output_device("default")

	def sweepImage(self, imageData, sweepDuration=0.5):
		with self._lavServer:
			totalVolumes=[0]*self._width
			for y in range(self._height):
				index=-1-y;
				lavWave = self._lavWaves[index]
				lavWave.mul=0
				envelopeValues=[0]
				for x in range(self._width):
					px = imageData[y][x]
					if self._reverseBrightness:
						px =1 - px
					envelopeValues.append(px)
				envelopeValues.append(0)
				totalVolumes[x]+=px
				lavWave.mul.envelope(time=0, duration=sweepDuration, values=envelopeValues)
			for index,totalVolume in enumerate(totalVolumes):
				totalVolumes[index]=0.075 if totalVolume<=1.0 else 0.075/totalVolume 
			self._lavPanner.mul=0.5
			self._lavPanner.azimuth=-90
			self._lavPanner.azimuth.linear_ramp_to_value(sweepDuration, 91)


import ctypes
import itertools
from legacy_level import *

class Level(object):

	PATH_TEMPLATE="levels/%02d"
	legacyLevel=None

	def __init__(self,levelNumber):
		self._loadFromPath(self.PATH_TEMPLATE%levelNumber)
		self.levelNumber=levelNumber

	def _loadFromPath(self,path):
		with open(path,'rb') as f:
			baseData=f.read()
		buffer=ctypes.c_buffer(baseData)
		self.legacyLevel=LEGACY_LEVEL.from_address(ctypes.addressof(buffer))
		self.legacyLevel._origRaw=baseData
		self.legacyLevel._curRaw=buffer

	def __getstate__(self):
		delta={}
		index=0
		for old,new in itertools.izip(self.legacyLevel._origRaw,self.legacyLevel._curRaw):
			if new!=old:
				delta[index]=new
			index+=1
		return (self.levelNumber,delta)

	def __setstate__(self,(levelNumber,delta)):
		self._loadFromPath(self.PATH_TEMPLATE%levelNumber)
		for index,val in delta.iteritems():
			self.legacyLevel._curRaw[index]=val
		self.levelNumber=levelNumber

	def __getattr__(self,name):
		return getattr(self.legacyLevel,name)

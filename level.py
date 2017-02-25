import ctypes
import itertools
from legacy_level import *

class Level(object):

	legacyLevel=None
	path=None

	def __init__(self,path):
		self._loadFromPath(path)

	def _loadFromPath(self,path):
		self.path=path
		self.levelNo=int(self.path[-2:])
		self.nextLevelPath=self.path[:-2]+("%02d"%(self.levelNo+1))
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
		return (self.path,delta)

	def __setstate__(self,(path,delta)):
		self._loadFromPath(path)
		for index,val in delta.iteritems():
			self.legacyLevel._curRaw[index]=val

	def __getattr__(self,name):
		return getattr(self.legacyLevel,name)

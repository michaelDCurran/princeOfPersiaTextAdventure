from ctypesUtil import unpackCTypesArray, readCtype
from legacy_level import *

class Level(object):

	@classmethod
	def fromFile(cls,path):
		level=cls(path)
		return level

	def __init__(self,path):
		self.path=path
		self.levelNo=int(self.path[-2:])
		self.nextLevelPath=self.path[:-2]+("%s"%(self.levelNo+1))
		f=open(path,'rb')
		legacyLevel=readCtype(f,LEGACY_LEVEL)
		for k in dir(legacyLevel):
			if k.startswith('_'): continue
			v=getattr(legacyLevel,k)
			v=unpackCTypesArray(v)
			setattr(self,k,v)


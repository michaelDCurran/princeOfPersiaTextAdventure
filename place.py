from legacy_level import *

LEFT=LD_LEFT
RIGHT=LD_RIGHT
UP=LD_ABOVE
DOWN=LD_BELOW

directionLabels={
	LEFT:"left",
	RIGHT:"right",
	UP:"up",
	DOWN:"down",
}

oppositeDirections={LEFT:RIGHT,RIGHT:LEFT,UP:DOWN,DOWN:UP}

class EdgeError(Exception):
	def __init__(self,place):
		self.place=place
		super(EdgeError,self).__init__()

class LevelExit(Exception):
		pass

def getLinkedRoom(direction,level,room):
	return level.link[room][direction]-1

from tile import *
from guard import *

class Place(object):

	@classmethod
	def fromEvent(self,level,ID):
		room=((level.door_2[ID]>>3)|((level.door_1[ID]&0x60)>>5))-1
		l=level.door_1[ID]&0x1f
		floor=l/PLACES
		place=l%PLACES
		return Place(level,room,floor,place)

	def __init__(self,level,room,floor,place):
		self.level,self.room,self.floor,self.place=level,int(room),int(floor),int(place)

	@property
	def guard(self):
		roomGuard=self.level.guard_location[self.room]
		guardFloor=roomGuard/PLACES
		guardPlace=roomGuard%PLACES
		if guardFloor==self.floor and guardPlace==self.place:
			return Guard(self)

	def isNameMatch(self,name):
		name=name.lower()
		if name.endswith(' above'):
			roof=self.getNextPlace(UP)
			if roof and name[:-6]==self.tile.roofName.lower():
				return True
		newStateDesc=self.tile.stateDescription.lower()
		newName=self.tile.name.lower()
		if (newStateDesc and name==(newStateDesc+" "+newName)) or name==newName: 
			return True
		return False

	@property
	def _lt(self):
		return self.level.foretable[self.room][self.floor][self.place]&0x1f

	@_lt.setter
	def _lt(self,t):
		self.level.foretable[self.room][self.floor][self.place]=t

	@property
	def _lm(self):
		return self.level.backtable[self.room][self.floor][self.place]

	@_lm.setter
	def _lm(self,m):
		self.level.backtable[self.room][self.floor][self.place]=m

	@property
	def tile(self):
		tileClass=tileMap[self._lt][0]
		return tileClass(self)

	def hasClearDirection(self,direction):
		newPlace=self.getNextPlace(direction)
		return newPlace and newPlace.tile.isEmpty

	def getNextPlace(self,direction):
		level,room,floor,place=self.level,self.room,self.floor,self.place
		if direction==LEFT:
			if place>0:
				place-=1
			else:
				newRoom=getLinkedRoom(direction,level,room)
				if newRoom<0:
					return
				room=newRoom
				place=PLACES-1
		elif direction==RIGHT:
			if place<(PLACES-1):
				place+=1
			else:
				newRoom=getLinkedRoom(direction,level,room)
				if newRoom<0:
					return
				room=newRoom
				place=0
		elif direction==UP:
			if floor>0:
				floor-=1
			else:
				newRoom=getLinkedRoom(direction,level,room)
				if newRoom<0:
					return
				room=newRoom
				floor=FLOORS-1
		elif direction==DOWN:
			if floor<(FLOORS-1):
				floor+=1
			else:
				newRoom=getLinkedRoom(direction,level,room)
				if newRoom<0:
					return
				room=newRoom
				floor=0
		return Place(self.level,room,floor,place)

	@property
	def description(self):
		t=self.tile
		msg=t.name
		stateDesc=self.tile.stateDescription
		if stateDesc:
			msg=stateDesc+" "+msg
		ornamentDescription=self.tile.ornamentDescription
		if ornamentDescription:
			msg+=" with %s"%ornamentDescription
		return msg

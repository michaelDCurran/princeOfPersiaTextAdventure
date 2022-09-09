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
		self.placeNum=place
		super(EdgeError,self).__init__()

class LevelExit(Exception):
		pass

from tile import *
from guard import *

class Place:

	@classmethod
	def fromEvent(self,level,ID):
		roomNum = ((level.door_2[ID]>>3)|((level.door_1[ID]&0x60)>>5))-1
		l=level.door_1[ID]&0x1f
		floorNum = l/PLACES
		placeNum = l%PLACES
		room = Room(level, roomNum)
		return Place(room, floorNum, placeNum)

	def __init__(self, room, floorNum, placeNum):
		if not isinstance(room,Room):
			raise TypeError(f"room must be of type {Room}")
		self.room = room
		self.floorNum = int(floorNum)
		self.placeNum = int(placeNum)

	@property
	def roomNum(self):
		return self.room.roomNum

	@property
	def level(self):
		return self.room.level

	@property
	def guard(self):
		roomGuard=self.level.guard_location[self.roomNum]
		guardFloor=roomGuard/PLACES
		guardPlace=roomGuard%PLACES
		if guardFloor==self.floorNum and guardPlace==self.placeNum:
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
		return self.level.foretable[self.roomNum][self.floorNum][self.placeNum]&0x1f

	@_lt.setter
	def _lt(self,t):
		self.level.foretable[self.roomNum][self.floorNum][self.placeNum]=t

	@property
	def _lm(self):
		return self.level.backtable[self.roomNum][self.floorNum][self.placeNum]

	@_lm.setter
	def _lm(self,m):
		self.level.backtable[self.roomNum][self.floorNum][self.placeNum]=m

	@property
	def tile(self):
		tileClass=tileMap[self._lt][0]
		return tileClass(self)

	def hasClearDirection(self,direction):
		newPlace=self.getNextPlace(direction)
		return newPlace and newPlace.tile.isEmpty

	def getNextPlace(self,direction):
		level,room,floor,place=self.level,self.room,self.floorNum,self.placeNum
		if direction==LEFT:
			if place>0:
				place-=1
			else:
				newRoom=self.room.getLinkedRoom(direction)
				if newRoom is None:
					return
				room=newRoom
				place=PLACES-1
		elif direction==RIGHT:
			if place<(PLACES-1):
				place+=1
			else:
				newRoom=self.room.getLinkedRoom(direction)
				if newRoom is None:
					return
				room=newRoom
				place=0
		elif direction==UP:
			if floor>0:
				floor-=1
			else:
				newRoom=self.room.getLinkedRoom(direction)
				if newRoom is None:
					return
				room=newRoom
				floor=FLOORS-1
		elif direction==DOWN:
			if floor<(FLOORS-1):
				floor+=1
			else:
				newRoom=self.room.getLinkedRoom(direction)
				if newRoom is None:
					return
				room=newRoom
				floor=0
		return Place(room,floor,place)

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


roomImageWidth = tileImageWidth * 10
roomImageHeight = (tileImageHeight * 3) + 4

class Room(object):

	def __init__(self, level, roomNum):
		self.level = level
		self.roomNum = roomNum

	def getLinkedRoom(self, direction):
		roomNum = self.level.link[self.roomNum][direction]-1
		if roomNum < 0:
			return None
		return Room(self.level, roomNum)

	def _placeTileImageInRoomImage(self, y,x,image,block):
		for i in range(tileImageHeight):
			for j in range(tileImageWidth):
				realX=x+j
				if realX<0 or realX>=60:
					continue
				realY=y+i
				if realY<0 or realY>=37:
					continue
				image[realY][realX]=block[i][j]/4

	def generateImage(self, kid):
		image = [[0]*roomImageWidth for y in range(roomImageHeight)]
		for f in range(3):
			places=[]
			for p in range(10):
				places.append(Place(self, f, p))
			try:
				prevPlace=places[0].getNextPlace(LEFT)
			except:
				prevPlace=None
			places.insert(0,prevPlace)
			for p in range(11):
				place=places[p]
				if place:
					if f==0: # top level, also do roof
						try:
							roof=place.getNextPlace(UP)
						except:
							roof=None
						if roof:
							block=roof.tile.generateImage()
							self._placeTileImageInRoomImage(1-tileImageHeight,-3+p*tileImageWidth,image,block)
					block = place.tile.generateImage()
					if f==kid.place.floorNum and (p-1)==kid.place.placeNum:
						kid.superimposeOnTileImage(block)
					guard=place.guard
					if guard:
						guard.superimposeOnTileImage(block)
					self._placeTileImageInRoomImage((f*tileImageHeight)+1,-3+p*tileImageWidth,image,block)
		return image

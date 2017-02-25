from place import *

class KidDeath(Exception):
	pass

class Kid(object):

	hasSword=False

	def getNextPlaceOrDie(self,place,direction):
		newPlace=place.getNextPlace(direction)
		if not newPlace:
			self.die()
		return newPlace

	def __init__(self,levelPath):
		self.alive=True
		self.healthPoints=3
		self.possibleHealthPoints=3
		self.loadLevel(levelPath)

	def printHealth(self):
		if self.alive:
			print "Health points: %d of %d"%(self.healthPoints,self.possibleHealthPoints)
		else:
			print "Dead"

	def increasePossibleHealthPoints(self,points):
		self.possibleHealthPoints+=points
		self.healthPoints=self.possibleHealthPoints
		self.printHealth()

	def changeHealthPoints(self,points):
		points=min(points,self.possibleHealthPoints-self.healthPoints)
		self.healthPoints+=points
		if points>0:
			print "Gained %d health points"%points
		elif points<0:
			print "Lost %d health points"%abs(points)
		if self.healthPoints<=0:
			self.die()
		self.printHealth()

	def pickUpItem(self):
		t=self.place.tile
		if isinstance(t,Tile_item):
			t.take()
			print "took "+t.name
			t.affectKid(self)
		else:
			print "Nothing to take"

	def printPlace(self,place=None,includeAbove=True):
		if not place:
			place=self.place
		msg=""
		if place.guard:
			msg+="guard, "
		if place.tile.isEmpty:
			bottom,floorCount=place.tile.findBottom()
			msg+=("%d story drop to %s below"%(floorCount,bottom.description if bottom else "abis"))
		else:
			msg+=place.description
		if includeAbove:
			above=place.getNextPlace(UP)
			if above:
				if not above.tile.isEmpty:
					msg+=", "+above.tile.roofName+" above"
					if above.hasClearDirection(oppositeDirections[self.direction]):
						msg+=" starts"
					elif above.hasClearDirection(self.direction):
						msg+=" ends"
		print msg

	def printDirection(self):
		print "Facing %s"%directionLabels[self.direction]

	def exit(self):
		if isinstance(self.place.tile,Tile_exit):
			if self.place.tile.isOpen:
				print "Walking through Exit"
				raise LevelExit
			else:
				print "Exit is closed"
		else:
			print "Not at exit"

	def die(self):
		self.alive=False
		print "Dead"
		raise KidDeath

	def touchPlace(self,vMomentum,hMomentum,continuing=False,grab=None):
		if self.place.tile.isEmpty:
			self.doPossibleFall(grab=grab)
			return
		if grab: grab=False
		if vMomentum>0:
			print "Landed on ",
		self.printPlace()
		self.doPossibleHarm(vMomentum,hMomentum)
		self.place.tile.touch()
		if self.place.tile.isEmpty and (not continuing or hMomentum<2):
			return self.doPossibleFall()
		if not continuing:
			ahead=self.place.getNextPlace(self.direction)
			if ahead:
				print "Ahead: ",
				above=self.place.getNextPlace(UP)
				includeAbove=above and above.tile.isEmpty
				self.printPlace(place=ahead,includeAbove=includeAbove)

	def doPossibleHarm(self,vMomentum,hMomentum):
		if self.place.guard:
			print "(Hit by guard)"
			self.die()
		if self.place.tile.willKillActer(vMomentum,hMomentum):
			self.die()
		elif self.place.tile.willHarmActer(vMomentum,hMomentum):
			self.changeHealthPoints(-1)

	def doPossibleGrab(self):
		newPlace=self.place.getNextPlace(self.direction)
		if not newPlace or not newPlace.tile.isFloor:
			return False
		self.place=newPlace
		print "grabbed onto ledge on %s and climbed up"%directionLabels[self.direction]
		self.touchPlace(0,1,grab=False)
		return True

	def doPossibleFall(self,grab=False):
		floorCount=0
		while self.place.tile.isEmpty:
			if grab and floorCount<2 and self.doPossibleGrab():
				return True
			print "Falling down"
			self.place=self.getNextPlaceOrDie(self.place,DOWN)
			floorCount+=1
		if floorCount>0:
			self.touchPlace(floorCount,0)
		return floorCount>0

	def step(self,grab=None):
		newPlace=self.getNextPlaceOrDie(self.place,self.direction)
		if newPlace.tile.isWall:
			print "Can't go that way - ahead: ",
			self.printPlace(place=newPlace,includeAbove=False)
			return
		self.place=newPlace
		self.touchPlace(0,1,grab=grab)

	def _walkRun(self,maxPlaces,stopAtName,run=False):
		minPlaces=2 if run else 1
		placeCount=0
		floorCount=0
		msg="Running" if run else "Walking"
		if maxPlaces is not None:
			msg+=" %s %d places"%(directionLabels[self.direction],maxPlaces)
		else:
			msg+=" %s"%directionLabels[self.direction]
			maxPlaces=LROOMS*PLACES
		if stopAtName:
			msg+=" until at %s"%stopAtName
		print msg+":"
		continuing=True
		hMomentum=2
		while continuing or placeCount<minPlaces:
			newPlace=self.getNextPlaceOrDie(self.place,self.direction)
			if newPlace.tile.isWall:
				print "Can't go that way - ahead: ",
				self.printPlace(place=newPlace,includeAbove=False)
				break
			self.place=newPlace
			placeCount+=1
			print "%s: "%placeCount,
			continuing=placeCount<maxPlaces
			if continuing:
				if stopAtName:
					if stopAtName=="edge" and self.place.hasClearDirection(self.direction):
						continuing=False
					elif self.place.isNameMatch(stopAtName):
						continuing=False
				if continuing and placeCount>=1:
					nextPlace=self.place.getNextPlace(self.direction)
					if nextPlace and nextPlace.tile.isWall:
						continuing=False
					elif not run and (not nextPlace or nextPlace.tile.isEmpty):
						continuing=False
			oldHealthPoints=self.healthPoints
			oldFloor=self.place.floor
			self.touchPlace(0,hMomentum,continuing=continuing)
			if self.healthPoints!=oldHealthPoints or self.place.floor!=oldFloor:
				break

	def walk(self,maxPlaces=None,stopAtName=None):
		self._walkRun(maxPlaces,stopAtName)

	def run(self,maxPlaces=None,stopAtName=None):
		self._walkRun(maxPlaces,stopAtName,run=True)

	def killGuard(self):
		nextPlace=self.place.getNextPlace(self.direction)
		if not nextPlace or not nextPlace.guard:
			print "No guard to kill"
		elif not self.hasSword:
			print "Nothing to kill guard with"
		else:
			nextPlace.guard.kill()

	def climbDown(self):
		backDirection=oppositeDirections[self.direction]
		newPlace=self.place.getNextPlace(backDirection)
		if not newPlace or not newPlace.tile.isEmpty:
			print "No drop behind"
			return False
		self.place=self.getNextPlaceOrDie(newPlace,DOWN)
		print "Climbing down backwards on %s"%directionLabels[backDirection]
		if self.place.tile.isEmpty:
			newPlace=self.place.getNextPlace(self.direction)
			if newPlace and not newPlace.tile.isWall:
				self.place=newPlace
				print "Swung in underneath"
		self.touchPlace(1,0)
		return True

	def climbUp(self):
		if isinstance(self.place.tile,Tile_exit):
			if self.place.tile.isOpen:
				print "Walking through Exit"
				raise LevelExit
			else:
				print "Exit is closed"
		above=self.place.getNextPlace(UP)
		if not above:
			print "Nothing to climb up to"
			return False
		elif above.tile.isEmpty:
			aheadAbove=above.getNextPlace(self.direction)
			if aheadAbove.tile.isFloor:
				if not aheadAbove.tile.isWall:
					self.place=aheadAbove
					print "climbed up to ledge on %s"%directionLabels[self.direction]
					self.touchPlace(0,0)
					return True
				print "Blocked by %s"%aheadAbove.description
				return False
			print "Nothing to climb up to"
			return False
		elif isinstance(above.tile,Tile_looseBoard):
			print "Bumped loose board"
			above.tile.touch()
			self.changeHealthPoints(-1)
			return False
		elif not above.tile.isWall and above.hasClearDirection(oppositeDirections[self.direction]):
			behind=self.place.getNextPlace(oppositeDirections[self.direction])
			if not behind or behind.tile.isWall:
				print "bumped roof"
				aheadAbove=above.getNextPlace(self.direction)
				if aheadAbove and isinstance(aheadAbove.tile,Tile_looseBoard):
					print "Bumped loose board in roof ahead"
					aheadAbove.tile.touch()
				return False
			self.place=above
			print "Climbed up to ledge directly above"
			self.touchPlace(0,0)
			return True
		print "bumped roof"
		aheadAbove=above.getNextPlace(self.direction)
		if aheadAbove and isinstance(aheadAbove.tile,Tile_looseBoard):
			print "Bumped loose board in roof ahead"
			aheadAbove.tile.touch()
		return False

	def turn(self):
		self._faceDirection(oppositeDirections[self.direction])

	def turnLeft(self):
		return self._faceDirection(LEFT)

	def turnRight(self):
		return self._faceDirection(RIGHT)

	def _faceDirection(self,direction):
		if self.direction!=direction:
			self.direction=direction
			self.printDirection()
			self.printPlace()
			ahead=self.place.getNextPlace(self.direction)
			if ahead:
				print "Ahead: ",
				self.printPlace(place=ahead)
			return True
		return False

	def leap(self,large=False,grab=False):
		print "leaping %s"%directionLabels[self.direction]
		places=2 if large else 1
		placeCount=0
		while placeCount<places:
			newPlace=self.getNextPlaceOrDie(self.place,self.direction)
			if newPlace.guard:
				print "(Hit by guard)"
				self.die()
			if newPlace.tile.isWall:
				print "Hit "+newPlace.description
				if placeCount>0:
					self.touchPlace(1,1,grab=grab)
				return False
			self.place=newPlace
			print self.place.tile.passVerb+" "+self.place.tile.name
			placeCount+=1
		newPlace=self.getNextPlaceOrDie(self.place,self.direction)
		if newPlace.tile.isWall:
			print "Hit "+newPlace.description
		else:
			self.place=newPlace
		self.touchPlace(1,1,grab=grab)
		return True

	@classmethod
	def loadFromRestorePoint(cls,saveState):
		import cPickle as pickle
		kid=pickle.loads(saveState)
		if not isinstance(kid,cls):
			raise ValueError("file was not a Kid")
		kid.lastRestorePoint=saveState
		return kid

	@classmethod
	def loadFromFile(cls,path):
		with open(path,'rb') as f:
			s=f.read()
			return cls.loadFromRestorePoint(s)

	def _createRestorePoint(self):
		import cPickle as pickle
		return pickle.dumps(self)

	def saveToFile(self,path):
		with open(path,"wb") as f:
			s=self._createRestorePoint()
			f.write(s)

	def loadLevel(self,path):
		level=Level(path)
		self.place=Place(level,level.start_position[0]-1,level.start_position[1]/PLACES,level.start_position[1]%PLACES)
		self.direction=RIGHT if level.start_position[2] else LEFT
		self.lastRestorePoint=self._createRestorePoint()

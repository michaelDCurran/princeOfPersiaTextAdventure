from level import *
from place import *

tileImageWidth = 6
tileImageHeight = 11

class Tile(object):

	def generateImage(self):
		block=[]
		for i in range(tileImageHeight):
			block.append([0]*tileImageWidth)
		return block

	def __init__(self,place):
		self.place=place

	isFloor=False
	isWall=False
	passVerb="over"

	@property
	def name(self):
		raise NotImplementedError

	roofName="roof"

	stateDescription=""

	@property
	def isEmpty(self):
		return not self.isFloor and not self.isWall

	@property
	def ornamentDescription(self):
		return tileMap[self.place._lt][1] or ""

	def willKillActer(self,vMomentum,hMomentum):
		return False

	def willHarmActer(self,vMomentum,hMomentum):
		return 0

	def touch(self):
		pass

class Tile_empty(Tile):
	name="drop"

	def findBottom(self):
		floorCount=0
		place=self.place
		while place and place.tile.isEmpty:
			place=place.getNextPlace(DOWN)
			floorCount+=1
		return (place,floorCount)

	def findClosestEdge(self, direction):
		distance=0
		place=self.place
		while place and place.tile.isEmpty:
			place=place.getNextPlace(direction)
			distance+=1
		return (place,distance)

class Tile_floor(Tile):

	def generateImage(self):
		block=super(Tile_floor,self).generateImage()
		for x in range(tileImageWidth):
			block[-1][x]=4
		return block

	name="floor"
	isFloor=True

	def willKillActer(self,vMomentum,hMomentum):
		if vMomentum>=3:
			return True
		return super(Tile_floor,self).willKillActer(vMomentum,hMomentum)

	def willHarmActer(self,vMomentum,hMomentum):
		if vMomentum>=2:
			return 1
		return super(Tile_floor,self).willHarmActer(vMomentum,hMomentum)

class Tile_pillar(Tile_floor):

	def generateImage(self):
		block=[]
		for i in range(tileImageHeight):
			block.append([0,2,2,2,2,0])
		block[-1]=[4,4,4,4,4,4]
		return block

class Tile_spikes(Tile_floor):
	name="spikes"

	def generateImage(self):
		block=super(Tile_spikes,self).generateImage()
		block[-2]=[4,0,4,0,4,0]
		block[-3]=[4,0,4,0,4,0]
		block[-4]=[3,0,3,0,3,0]
		block[-5]=[2,0,2,0,2,0]
		return block

	def willKillActer(self,vMomentum,hMomentum):
		if vMomentum>=2 or hMomentum>=2:
			return True
		return super(Tile_spikes,self).willKillActer(vMomentum,hMomentum)

class Tile_chopper(Tile_floor):
	name="chopper"
	isTall=True
	passVerb="through"

	def willKillActer(self,vMomentum,hMomentum):
		return True

class Tile_item(Tile_floor):

	def take(self):
		self.place._lt=LT_FLOOR

	def affectKid(self,acter):
		pass

class Tile_sword(Tile_item):
	name="sword"

	def generateImage(self):
		block=super(Tile_sword,self).generateImage()
		block[-3]=[3,3,0,0,0,0]
		block[-4]=[4,4,3,3,3,0]
		block[-5]=[4,4,0,0,0,0]
		return block

	def affectKid(self,acter):
		acter.hasSword=True

class Tile_potion(Tile_item):
	name="potion"

	def generateImage(self):
		block=super(Tile_floor,self).generateImage()
		block[-1]=[4,4,4,4,4,4]
		block[-2]=[0,0,4,4,4,0]
		block[-3]=[0,0,4,4,4,0]
		block[-4]=[0,0,4,4,4,0]
		block[-5]=[0,0,0,3,0,0]
		block[-6]=[0,0,0,3,0,0]
		block[-7]=[0,0,3,0,3,0]
		block[-8]=[0,0,0,3,0,0]
		return block

	_potionStateDescriptions={
		LM_POTION_EMPTY:"empty",
		LM_POTION_HEALTH_POINT:"small red",
		LM_POTION_LIFE:"big red",
		LM_POTION_FEATHER_FALL:"green",
		LM_POTION_INVERT:"empty",
		LM_POTION_POISON:"blue",
		LM_POTION_OPEN:"empty",
	}

	@property
	def stateDescription(self):
		return self._potionStateDescriptions[self.place._lm]

	def affectKid(self,acter):
		lm=self.place._lm
		if lm==LM_POTION_HEALTH_POINT:
			acter.changeHealthPoints(1)
		elif lm==LM_POTION_LIFE:
			acter.increasePossibleHealthPoints(1)
		elif lm==LM_POTION_POISON:
			acter.changeHealthPoints(-1)

class Tile_looseBoard(Tile_floor):
	name="loose floor"
	roofName="loose tile"

	def generateImage(self):
		block=super(Tile_looseBoard,self).generateImage()
		block[-1]=[3,1,3,1,3,1]
		return block

	def touch(self):
		self.place._lt=LT_EMPTY
		print("(loose floor fell)")
		place=self.place
		numStories = 0
		while place.tile.isEmpty:
			numStories += 1
			place=place.getNextPlace(DOWN)
			if not place:
				break
		if place:
			landedOn = place.tile.name
			print(f"(loose floor landed on {landedOn} {numStories} stories below)")
			place.tile.touch()

class Tile_stuckButton(Tile_floor):
	name="stuck button"

class Tile_button(Tile_floor):

	def generateImage(self):
		block=super(Tile_button,self).generateImage()
		block[-2]=[2,3,3,3,3,2]
		return block

class Tile_dropButton(Tile_button):
	name="floor button"

	def touch(self):
		print("(button activated)")
		place=self.place.fromEvent(self.place.level,self.place._lm)
		place.tile.setOpenState(False)

class Tile_raiseButton(Tile_button):
	name="raise button"

	def touch(self):
		print("(button activated)")
		place=self.place.fromEvent(self.place.level,self.place._lm)
		place.tile.setOpenState(True)

class Tile_door(Tile_floor):

	name="door"
	isOpen=False
	isObstructive=False

	def generateImage(self):
		block=super(Tile_door,self).generateImage()
		for i in range(tileImageHeight):
			for j in range(tileImageWidth):
				val=0
				if j==0 or j==(tileImageWidth-1):
					val=4
				elif i%2==0:
					val=4 if not self.isOpen or i==0 else 0
				block[i][j]=val
		return block

	@property
	def passVerb(self):
		return "through" if self.isObstructive else "past"

	@property
	def isWall(self):
		return self.isObstructive and not self.isOpen

	def setOpenState(self,isOpen):
		raise NotImplementedError

	@property
	def stateDescription(self):
		return "open" if self.isOpen else "closed"

class Tile_gate(Tile_door):
	name="gate"
	isObstructive=True
	isTall=True

	@property
	def isOpen(self):
		return self.place._lm==LM_GATE_OPEN

	def setOpenState(self,isOpen):
		if isOpen!=self.isOpen:
			if isOpen:
				print("(Gate opened)")
				self.place._lm=LM_GATE_OPEN
			else:
				print("(gate closed)")
				self._lm=LM_GATE_CLOSED

class Tile_exit(Tile_door):
	name="Exit"
	isObstructive=False

	@property
	def isOpen(self):
		return self.place._lm==LM_EXIT_MOST_OPEN

	def setOpenState(self,isOpen):
		if isOpen!=self.isOpen:
			if isOpen:
				print("(Exit opened)")
				self.place._lm=LM_EXIT_MOST_OPEN
			else:
				print("(Exit closed)")
				self._lm=LM_EXIT_CLOSED

class Tile_wall(Tile):
	name="wall"
	isWall=True

	def generateImage(self):
		block=super(Tile_wall,self).generateImage()
		for i in range(tileImageHeight):
			for j in range(tileImageWidth):
				block[i][j]=4
		return block

class Tile_mirror(Tile_wall):
	name="mirror"
	passVerb="through"

tileMap={
	LT_EMPTY:(Tile_empty,None),
	LT_FLOOR:(Tile_floor,None),
	LT_SPIKES:(Tile_spikes,None),
	LT_PILLAR:(Tile_pillar,"pillar"),
	LT_GATE:(Tile_gate,None),
	LT_STUCK_BUTTON:(Tile_stuckButton,None),
	LT_DROP_BUTTON:(Tile_dropButton,None),
	LT_TAPESTRY:(Tile_wall,"tapestry"),
	LT_BOTTOM_BIG_PILLAR:(Tile_floor,"giant pillar"),
	LT_TOP_BIG_PILLAR:(Tile_empty,"giant pillar"),
	LT_POTION:(Tile_potion,None),
	LT_LOOSE_BOARD:(Tile_looseBoard,None),
	LT_TAPESTRY_TOP:(Tile_wall,"tapestry"),
	LT_MIRROR:(Tile_mirror,None),
	LT_DEBRIS:(Tile_floor,"debris"),
	LT_RAISE_BUTTON:(Tile_raiseButton,None),
	LT_EXIT_LEFT:(Tile_exit,None),
	LT_EXIT_RIGHT:(Tile_exit,None),
	LT_CHOPPER:(Tile_chopper,None),
	LT_TORCH:(Tile_floor,"torch"),
	LT_WALL:(Tile_wall,None),
	LT_SKELETON:(Tile_floor,"skeleton"),
	LT_SWORD:(Tile_sword,None),
	LT_BALCONY_LEFT:(Tile_empty,"balcony"),
	LT_BALCONY_RIGHT:(Tile_empty,"balcony"),
	LT_LATTICE_PILLAR:(Tile_floor,"lattice pillar"),
	LT_LATTICE_SUPPORT:(Tile_empty,"lattice support"),
	LT_SMALL_LATTICE:(Tile_empty,"small lattice"),
	LT_LATTICE_LEFT:(Tile_empty,"lattice"),
	LT_LATTICE_RIGHT:(Tile_empty,"lattice"),
	LT_TORCH_WITH_DEBRIS:(Tile_floor,"torch and debris"),
}

from level import *
from place import *

class Tile(object):

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

class Tile_floor(Tile):

	name="floor"
	isFloor=True
	roofName="floor"

	def willKillActer(self,vMomentum,hMomentum):
		if vMomentum>=3:
			return True
		return super(Tile_floor,self).willKillActer(vMomentum,hMomentum)

	def willHarmActer(self,vMomentum,hMomentum):
		if vMomentum>=2:
			return 1
		return super(Tile_floor,self).willHarmActer(vMomentum,hMomentum)

class Tile_spikes(Tile_floor):
	name="spikes"

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

	def affectKid(self,acter):
		acter.hasSword=True

class Tile_potion(Tile_item):
	name="potion"

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

	def touch(self):
		self.place._lt=LT_EMPTY
		print "(loose floor fell)"
		place=self.place
		while place.tile.isEmpty:
			place=place.getNextPlace(DOWN)
			if not place:
				return
		print "(loose floor landed on %s below)"%place.tile.name
		place.tile.touch()

class Tile_stuckButton(Tile_floor):
	name="stuck button"

class Tile_button(Tile_floor):
	pass

class Tile_dropButton(Tile_button):
	name="floor button"

	def touch(self):
		print "(button activated)"
		place=self.place.fromEvent(self.place.level,self.place._lm)
		place.tile.setOpenState(False)

class Tile_raiseButton(Tile_button):
	name="raise button"

	def touch(self):
		print "(button activated)"
		place=self.place.fromEvent(self.place.level,self.place._lm)
		place.tile.setOpenState(True)

class Tile_door(Tile_floor):

	name="door"
	isOpen=False
	isObstructive=False

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
				print "(Gate opened)"
				self.place._lm=LM_GATE_OPEN
			else:
				print "(gate closed)"
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
				print "(Exit opened)"
				self.place._lm=LM_EXIT_MOST_OPEN
			else:
				print "(Exit closed)"
				self._lm=LM_EXIT_CLOSED

class Tile_wall(Tile):
	name="wall"
	isWall=True

class Tile_mirror(Tile_wall):
	name="mirror"
	passVerb="through"

tileMap={
	LT_EMPTY:(Tile_empty,None),
	LT_FLOOR:(Tile_floor,None),
	LT_SPIKES:(Tile_spikes,None),
	LT_PILLAR:(Tile_floor,"pillar"),
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

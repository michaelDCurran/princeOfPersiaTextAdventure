from place import *

class Guard(object):

	def superimposeOnTileImage(self,block):
		block[-2]=[0,0,4,4,0,0]
		block[-3]=[0,0,4,4,0,0]
		block[-4]=[0,0,4,4,0,0]
		block[-5]=[0,0,4,4,0,0]
		block[-4][1 if self.direction==LEFT else 4]=4

	def __init__(self,place):
		self.place=place

	@property
	def direction(self):
		return self.place.level.guard_direction[self.place.roomNum]

	def kill(self):
		self.place.level.guard_location[self.place.roomNum]=FLOORS*PLACES
		print("(Guard died)")

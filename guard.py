from place import *

class Guard(object):

	def __init__(self,place):
		self.place=place

	def kill(self):
		self.place.level.guard_location[self.place.room]=FLOORS*PLACES
		print("(Guard died)")

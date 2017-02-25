import sys
import msvcrt
import re
import cmd
import time
import cPickle as pickle
from kid import *

class HandleInput(object):
 
	def do_save(self):
		"""Prompts for a path to save the current game."""
		path=raw_input("Enter file name to save to:")
		self.kid.saveToFile(path)

	def do_quit(self):
		"""Quits the game."""
		print "Good bye"
		sys.exit(0)

	def do_stepLeft(self):
		"""Moves left one place, or turns left if not facing that way."""
		if not self.kid.turnLeft():
			self.kid.step()

	def do_stepRight(self):
		"""Moves right one place, or turns left if not facing that way."""
		if not self.kid.turnRight():
			self.kid.step()

	def do_walkLeft(self):
		"""Continues walking left until reaching a drop or a wall."""
		self.kid.turnLeft()
		self.kid.walk()

	def do_walkRight(self):
		"""Continues walking right until reaching a drop or a wall."""
		self.kid.turnRight()
		self.kid.walk()

	def do_take(self):
		"""Picks up the item at your position."""
		self.kid.pickUpItem()

	def do_leapLeft(self):
		"""Jumps left 2 positions. Useful for crossing empty space. Automatically grabs onto a ledge ahead if just missing it by one position."""
		self.kid.turnLeft()
		self.kid.leap(grab=True)

	def do_leapRight(self):
		"""Jumps right 2 positions. Useful for crossing empty space. Automatically grabs onto a ledge ahead if just missing it by one position."""
		self.kid.turnRight()
		self.kid.leap(grab=True)

	def do_kill(self):
		"""Kills the guard directly ahead of you."""
		self.kid.killGuard()

	def do_climbUp(self):
		"""Climbs up to the ledge directly ahead of you or directly above when your back is at a drop."""
		self.kid.climbUp()

	def do_climbDown(self):
		"""Climb down behind you."""
		self.kid.climbDown()

	def do_help(self):
		"""Prints commands.""" 
		print "Available commands:"
		for key,name in self.keyCommands.iteritems():
			func=getattr(self,'do_'+name)
			help=func.__doc__
			print "%s (%s): %s"%(key,name,help)

	keyCommands={
		'q':"quit",
		's':"save",
		'h':"walkLeft",
		'j':"stepLeft",
		'l':"stepRight",
		';':"walkRight",
		'i':"climbUp",
		',':"climbDown",
		'y':"leapLeft",
		'p':"leapRight",
		'<':"take",
		'k':"kill",
		"?":"help",
	}

	def __init__(self,kid):
		self.kid=kid
		while True:
			#print "> ",
			ch=msvcrt.getch()
			funcName=self.keyCommands.get(ch)
			if funcName:
				func=getattr(self,'do_'+funcName)
				#print funcName 
				func()

if __name__=='__main__':
	print "Prince of Persia Text Adventure"
	levelNo=1
	if len(sys.argv)>1:
		loadPath=sys.argv[1]
		kid=Kid.loadFromFile(loadPath)
		print "Restored from %s"%loadPath
	else:
		kid=Kid('levels/06')
	while True:
		print "On level %d"%kid.place.level.levelNo
		kid.touchPlace(0,0)
		kid.printDirection()
		kid.printHealth()
		try:
			HandleInput(kid)
		except KidDeath:
			print "Press enter to restart"
			raw_input()
			kid=kid.loadFromRestorePoint(kid.lastRestorePoint)
			continue
		except LevelExit:
			print "Level complete"
			print "Press enter to proceed to next level"
			raw_input()
			kid.loadLevel(kid.place.level.nextLevelPath)

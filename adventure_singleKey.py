import sys
import msvcrt
import re
import cmd
import time
from imagePlayer import ImagePlayer
import pickle as pickle
from kid import *

class HandleInput:
 
	def do_save(self):
		"""Prompts for a path to save the current game."""
		path=input("Enter file name to save to:")
		self.kid.saveToFile(path)

	def do_quit(self):
		"""Quits the game."""
		print("Good bye")
		sys.exit(0)

	def do_stepLeft(self,grab=False):
		"""Moves left one place, or turns left if not facing that way."""
		if not self.kid.turnLeft():
			self.kid.step(grab=grab)

	def do_stepLeft_and_grab(self):
		return self.do_stepLeft(grab=True)
	do_stepLeft_and_grab.__doc__=do_stepLeft.__doc__+" Automatically grabs onto the closest ledge ahead if falling."

	def do_stepRight(self,grab=False):
		"""Moves right one place, or turns left if not facing that way."""
		if not self.kid.turnRight():
			self.kid.step(grab=grab)

	def do_stepRight_and_grab(self):
		return self.do_stepRight(grab=True)
	do_stepRight_and_grab.__doc__=do_stepRight.__doc__+" Automatically grabs onto the closest ledge ahead if falling."

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

	def do_leapLeft(self,grab=False):
		"""Jumps left 2 positions. Useful for crossing empty space."""
		self.kid.turnLeft()
		self.kid.leap(grab=grab)

	def do_leapLeft_and_grab(self):
		return self.do_leapLeft(grab=True)
	do_leapLeft_and_grab.__doc__=do_leapLeft.__doc__+" Automatically grabs onto the closest ledge ahead if just missing it."

	def do_leapRight(self,grab=False):
		"""Jumps right 2 positions. Useful for crossing empty space."""
		self.kid.turnRight()
		self.kid.leap(grab=grab)

	def do_leapRight_and_grab(self):
		return self.do_leapRight(grab=True)
	do_leapRight_and_grab.__doc__=do_leapRight.__doc__+" Automatically grabs onto the closest ledge ahead if just missing it."

	def do_kill(self):
		"""Kills the guard directly ahead of you."""
		self.kid.killGuard()

	def do_climbUp(self):
		"""Climbs up to the ledge directly ahead of you or directly above when your back is at a drop."""
		self.kid.climbUp()

	def do_climbDown(self):
		"""Climb down behind you."""
		self.kid.climbDown()

	def do_where(self):
		""" Reports level number, room number, floor and place."""
		kid.printWhere()

	def do_help(self):
		"""Prints commands.""" 
		print("Available commands:")
		for key,name in self.keyCommands.items():
			if key.isupper():
				key="Shift + %s"%(key.lower())
			func=getattr(self,'do_'+name)
			help=func.__doc__
			print("%s (%s): %s"%(key,name,help))

	def do_sonify(self):
		image = self.kid.place.room.generateImage(self.kid)
		sonifier.sweepImage(image, sweepDuration=5)

	keyCommands={
		b'q':"quit",
		b's':"save",
		b'h':"walkLeft",
		b'j':"stepLeft",
		b'J':"stepLeft_and_grab",
		b'l':"stepRight",
		b'L':"stepRight_and_grab",
		b';':"walkRight",
		b'i':"climbUp",
		b',':"climbDown",
		b'y':"leapLeft",
		b'Y':"leapLeft_and_grab",
		b'p':"leapRight",
		b'P':"leapRight_and_grab",
		b'<':"take",
		b'k':"kill",
		b"w": "where",
		b"?":"help",
		b"`": "sonify",
	}

	def __init__(self,kid):
		self.kid=kid
		while True:
			ch=msvcrt.getch()
			funcName=self.keyCommands.get(ch)
			if funcName:
				func=getattr(self,'do_'+funcName)
				func()

if __name__=='__main__':
	print("Prince of Persia Text Adventure")
	levelNumber=1
	if len(sys.argv)>1:
		loadPath=sys.argv[1]
		kid=Kid.loadFromFile(loadPath)
		print("Restored from %s"%loadPath)
	else:
		kid=Kid(levelNumber)
	sonifier = ImagePlayer(lowFreq=220, highFreq=7040, width=roomImageWidth, height=roomImageHeight)
	while True:
		print("On level %d"%kid.place.level.levelNumber)
		try:
			kid.touchPlace(0,0)
			kid.printDirection()
			kid.printHealth()
			HandleInput(kid)
		except KidDeath:
			print("Press enter to restart")
			input()
			kid=kid.loadFromRestorePoint(kid.lastRestorePoint)
			continue
		except LevelExit:
			print("Level complete")
			print("Press enter to proceed to next level")
			input()
			kid.loadNextLevel()

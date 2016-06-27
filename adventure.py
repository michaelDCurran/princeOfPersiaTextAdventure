import sys
import cmd
import re
import time
import cPickle as pickle
import msvcrt
from kid import *

class Commander(cmd.Cmd):

	prompt=">"

	_re_numPlaces=re.compile(r"(\d+) places?")
	_re_toPlace=re.compile(r"to (.+)")
	_lastBatchCommand=None

	def do_save(self,args):
		kid.saveToFile(args)
	do_save.__doc__="""save <fileName>
	Saves the current state of the game to a file for later reloading.
	"""

	def emptyline(self):
		print "What?"

	def onecmd(self,line):
		sublines=line.split(' then ')
		if len(sublines)>1:
			for subline in sublines:
				self.onecmd(subline)
				self._lastBatchCommand=self.parseline(subline)[0]
			self._lastBatchCommand=None
		else:
			cmd.Cmd.onecmd(self,line)

	def do_quit(self,args):
		print "Good bye"
		sys.exit(0)
	do_quit.__doc__="Quits the game!"

	def do_clock(self,args):
		print "Time elapsed: %02d:%02d"%(kid.clock/60,kid.clock%60)
	do_clock.__doc__="""Shows how much time has been spent. 
	Note that this is not real-world time, rather each action takes 1
	or more seconds to complete.
	E.g. running is faster than walking.
	"""

	def do_step(self,args):
		kid.walk(maxPlaces=1)
	do_step.__doc__="Alias for walk 1 place"

	def do_take(self,args):
		kid.pickUpItem()
	do_take.__doc__="""Picks up the item from the floor where you are standing.
	Examples:
	> take sword
	or
	> take potion
	"""

	def do_exit(self,args):
		kid.exit()
	do_exit.__doc__="Exits the level, if you are at an opened exit."

	def _do_walkRun(self,args,run=False):
		walkRun=kid.run if run else kid.walk
		if not args:
			walkRun()
			return
		m=self._re_numPlaces.match(args)
		if m:
			walkRun(maxPlaces=int(m.groups()[0]))
			return
		m=self._re_toPlace.match(args)
		if m:
			walkRun(stopAtName=m.groups()[0])
			return
		print "walk where?"

	def do_walk(self,args):
		self._do_walkRun(args)
	do_walk.__doc__="""walk [{how far|to where}]
	Walks 1 or more places.
	Examples:
	> walk
	(Walks until there is a danger)
	> walk 3 places
	(Walks 3 places)
	> walk to sword
	(Walks until at a sword)
	"""

	def do_run(self,args):
		self._do_walkRun(args,run=True)
	do_run.__doc__="""run [{how far|to where}]
	Runs 1 or more places.
	Similar to walk, but does not stop at dangers.
	It also takes less time, and avoids falling when stepping on loose boards.
	Examples:
	> run
	(runs continuously) 
	> run 3 places
	(runs 3 places)
	> run to sword
	(runs until at a sword)
	"""

	def _do_leap(self,args,large=False):
		large=self._lastBatchCommand=="run"
		kid.leap(large=large,grab=True)

	def do_leap(self,args):
		self._do_leap(args)
	do_leap.__doc__="""Leaps forward over the next place (E.g. a drop).
	Normally only 1 place is leaped. 
	However, it is possible to leap 2 places with a run-up by joining it onto the end of a run command:
	> run to edge then leap
	Which will leap 2 places rather than 1.
	If you still won't make the distance, try grabbing for the far edge:
	leap and grab
	or
	run to edge then leap and grab
	The full syntax is: [run [{how far|to where}] then ]leap [and grab] 
	"""

	def do_turn(self,args):
		kid.turn()
	do_turn.__doc__="Turns to the opposite direction."

	def do_kill(self,args):
		if args=="guard":
			kid.killGuard()
		else:
			print "Kill what?"
	do_kill.__doc__="""Kill something.
	Example:
	> kill guard
	An item may be required to kill something.
	"""

	def do_climb(self,args):
		if args=="up":
			kid.climbUp()
		elif args=="down":
			kid.climbDown()
		else:
			print "climb which way? [up or down]"
	do_climb.__doc__="""climb {up|down}
	Climb up onto a ledge, or down off a ledge.
	"""

if __name__=='__main__':
	print "Prince of Persia Level Walker"
	levelNo=1
	lastKidClock=0
	if len(sys.argv)>1:
		loadPath=sys.argv[1]
		kid=Kid.loadFromFile(loadPath)
		print "Restored from %s"%loadPath
	else:
		kid=Kid('levels/01')
	while True:
		print "On level %d"%kid.place.level.levelNo
		kid.touchPlace(0,0)
		kid.printDirection()
		kid.printHealth()
		commander=Commander()
		try:
			commander.cmdloop()
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

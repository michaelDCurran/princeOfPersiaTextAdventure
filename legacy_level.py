import ctypes
from ctypesUtil import readCtype

LROOMS=24
FLOORS=3
PLACES=10
LEVENTS=256

LT_EMPTY=0
LT_FLOOR=1
LT_SPIKES=2
LT_PILLAR=3
LT_GATE=4
LT_STUCK_BUTTON=5
LT_DROP_BUTTON=6
LT_TAPESTRY=7
LT_BOTTOM_BIG_PILLAR=8
LT_TOP_BIG_PILLAR=9
LT_POTION=10
LT_LOOSE_BOARD=11
LT_TAPESTRY_TOP=12
LT_MIRROR=13
LT_DEBRIS=14
LT_RAISE_BUTTON=15
LT_EXIT_LEFT=16
LT_EXIT_RIGHT=17
LT_CHOPPER=18
LT_TORCH=19
LT_WALL=20
LT_SKELETON=21
LT_SWORD=22
LT_BALCONY_LEFT=23
LT_BALCONY_RIGHT=24
LT_LATTICE_PILLAR=25
LT_LATTICE_SUPPORT=26
LT_SMALL_LATTICE=27
LT_LATTICE_LEFT=28
LT_LATTICE_RIGHT=29
LT_TORCH_WITH_DEBRIS=30
LT_NULL=31

LD_LEFT=0
LD_RIGHT=1
LD_ABOVE=2
LD_BELOW=3

LM_GATE_CLOSED=0
LM_GATE_OPEN=1

LM_EXIT_CLOSED=0X0
LM_EXIT_MOST_OPEN=0XFF

LM_POTION_EMPTY=0
LM_POTION_HEALTH_POINT=1
LM_POTION_LIFE=2
LM_POTION_FEATHER_FALL=3
LM_POTION_INVERT=4
LM_POTION_POISON=5
LM_POTION_OPEN=6

class LEGACY_LEVEL(ctypes.Structure):

	_pack_=1
	_fields_=(
		('foretable',((ctypes.c_uint8*PLACES)*FLOORS)*LROOMS),
		('backtable',((ctypes.c_uint8*PLACES)*FLOORS)*LROOMS),
		('door_1',ctypes.c_uint8*LEVENTS),
		('door_2',ctypes.c_uint8*LEVENTS),
		('link',(ctypes.c_uint8*4)*LROOMS),
		('unknown_1',ctypes.c_uint8*64),
		('start_position',ctypes.c_uint8*3),
		('unknown_2',ctypes.c_uint8*3),
		('unknown_3',ctypes.c_uint8),
		('guard_location',ctypes.c_uint8*LROOMS),
		('guard_direction',ctypes.c_uint8*LROOMS),
		('unknown_4a',ctypes.c_uint8*LROOMS),
		('unknown_4b',ctypes.c_uint8*LROOMS),
		('guard_skill',ctypes.c_uint8*LROOMS),
		('unknown_4c',ctypes.c_uint8*LROOMS),
		('guard_color',ctypes.c_uint8*LROOMS),
		('unknown_4d',ctypes.c_uint8*16),
		('signature',ctypes.c_uint8*2),
	)

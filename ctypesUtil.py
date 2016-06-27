from ctypes import *

def readCtype(f,ctype):
	s=sizeof(ctype)
	b=c_buffer(s)
	b.raw=f.read()
	a=addressof(b)
	v=ctype.from_address(a)
	v._buffer=b
	return v

def unpackCTypesArray(a):
	if not isinstance(a,Array):
		return a
	l=[]
	for x in a:
		l.append(unpackCTypesArray(x))
	return l

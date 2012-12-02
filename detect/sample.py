###############################################################################
# Event Detection Algorithm Suite
#  Copyright (C) 2012 Gian Perrone (http://github.com/gian)
#  
#  Permission to use, copy, modify, and distribute this software and its
#  documentation for any purpose and without fee is hereby granted,
#  provided that the above copyright notice appear in all copies and that
#  both the copyright notice and this permission notice and warranty
#  disclaimer appear in supporting documentation, and that the name of
#  the above copyright holders, or their entities, not be used in
#  advertising or publicity pertaining to distribution of the software
#  without specific, written prior permission.
#  
#  The above copyright holders disclaim all warranties with regard to
#  this software, including all implied warranties of merchantability and
#  fitness. In no event shall the above copyright holders be liable for
#  any special, indirect or consequential damages or any damages
#  whatsoever resulting from loss of use, data or profits, whether in an
#  action of contract, negligence or other tortious action, arising out
#  of or in connection with the use or performance of this software.
###############################################################################

from . import eventstream

class Sample(object):
	def __init__(self, ind=0, time=0, x=0, y=0):
		self.index = ind
		self.time = time
		self.x = x
		self.y = y

	def __str__(self):
		return "(%d,%f,%d,%d)" % (self.index, self.time, self.x, self.y)

	def __repr__(self):
		return self.__str__()

class SampleStream:
	def __init__(self):
		raise "SampleStream shouldn't be instantiated directly. Use FileSampleStream or ListSampleStream."

	def __iter__(self):
		return self

	def next(self):
		raise StopIteration

class ListSampleStream:
	def __init__(self,data):
		self.data = data
	
	def next(self):
		if len(self.data) == 0:
			raise StopIteration

		return self.data.pop(0)


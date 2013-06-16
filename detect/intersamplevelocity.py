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
from eventstream import EventStream

import math

class IntersampleVelocity(EventStream):
	"""
	    Annotate a stream of samples with a 'velocity' component,
	    which is computed as a simple intersample velocity between
	    temporally adjacent samples.
	"""
	def __init__(self, sampleStream):
		super(IntersampleVelocity, self).__init__(sampleStream)
		self.prev = self.input.next()

	def intersampleVelocity(self,prev,curr):
		dx = curr.x - prev.x
		dy = curr.y - prev.y
		dt = curr.time - prev.time

		if dt <= 0:
			# We can't work with a zero or negative time interval, so we
			# return zero. 
			return 0.0

		d = math.sqrt(dx * dx + dy * dy)

		return d / float(dt)
		
	def next(self):
		curr = self.input.next()

		curr.velocity = self.intersampleVelocity(self.prev,curr)

		self.prev = curr

		return curr



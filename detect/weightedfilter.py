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

class WeightedFilter(EventStream):
	"""
	    This implements a convolution of a filter consisting of n weights
	    over a given stream of input samples.  The significant change
	    is that it converts to velocities (i.e., speed and direction),
	    performs weighted filtering, and then converts back to idealised
	    (x,y) coordinates.

	    Parameters:
	    	tapWeights (list of floats) length determintes how many taps should be used.
	"""
	def __init__(self, sampleStream, tapWeights):
		super(WeightedFilter, self).__init__(sampleStream)
		self.tapWeights = self.normalize(tapWeights)
		self.window = []

	def normalize(self,weights):
		m = max(weights)
		return [x / m for x in weights]

	def intersampleVelocity(self,prev,curr):
		dx = curr.x - prev.x
		dy = curr.y - prev.y
		dt = curr.time - prev.time

		if dt <= 0:
			# We can't work with a zero or negative time interval, so we
			# return an arbitrary large velocity
			return 10000.0

		d = math.sqrt(dx * dx + dy * dy)

		return d / float(dt)
		

	def next(self):
		fixation = []

		for curr in self.input:
			v = self.intersampleVelocity(self.prev,curr)
			
			if v < self.threshold:
				fixation.append(self.prev)
				self.prev = curr
			elif len(fixation) == 0 and v >= self.threshold:
				# We're probably in a saccade.  Quietly discard.
				self.prev = curr
				continue
			else:
				# We have reached the end of a saccade.

				c = self.centroid(fixation)
				prev = self.prev
				self.prev = curr
				return EFixation(c,len(fixation),fixation[0],prev)

		# We have broken out of the iteration, which means we've reached end of input
		# We have to deal with any remaining samples in 'fixation'

		if len(fixation) == 0:
			raise StopIteration
		else:
			c = self.centroid(fixation)
			return EFixation(c,len(fixation),fixation[0],fixation.pop())



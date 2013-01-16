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

class MovingAverageFilter(EventStream):
	"""
		This is a naive smoothing filter, corresponding to an
		n-sample moving average over gaze points.

		Parameters:
			filterSize (samples)  The number of samples to average.
	"""
	def __init__(self, sampleStream, filterSize):
		super(MovingAverageFilter, self).__init__(sampleStream)
		self.window = []
		self.filterSize = filterSize

	def next(self):

		while len(self.window) < self.filterSize:
			self.window.append(self.input.next())

		p = self.centroid(self.window)

		# Slice off the first element.
		self.window = self.window[1:]

		return p


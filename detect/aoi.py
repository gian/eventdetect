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
from eventstream import EFixation

class AOI(EventStream):
	"""Areas of Interest event detection. 
	   
	   This is based on I-AOI of Salvucci and Goldberg (2000).

	   Parameters:
		threshold: (samples) the duration above which to consider a fixation.
		areas: A list of coordinate tuples denoting areas of interest.
		   Currently always rectangular, with the form:
		   (upperLeftX,upperLeftY,lowerRightX,lowerRightY)
	"""
	def __init__(self, sampleStream, threshold, areas):
		super(AOI, self).__init__(sampleStream)
		self.threshold = threshold
		self.areas = areas


	def inArea(self, p):
		for a in self.areas:
			if p.x >= a[0] and p.x <= a[2] and p.y >= a[1] and p.y <= a[3]:
				return a

		return None

	def next(self):

		samples = []
		currentArea = None

		for s in self.input:
			a = self.inArea(s)
			if a != None:
				if currentArea == None:
					currentArea = a
					samples.append(s)
				elif currentArea == a:
					samples.append(s)
				else:
					end = samples.pop()
					p = self.centroid(samples)
					length = len(samples)

					if length < self.threshold:
						samples = []
						currentArea = None
						continue
					else:
						return EFixation(p, length, samples[0], end)
					
			else:
				# Outside an area of interest
				currentArea = None
				if len(samples) > self.threshold:
					end = samples.pop()
					p = self.centroid(samples)
					return EFixation(p, len(samples), samples[0], end)
				else:
					samples = []
					continue
					

		raise StopIteration



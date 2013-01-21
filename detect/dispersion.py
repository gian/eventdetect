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

class Dispersion(EventStream):
	"""Simple dispersion-based algorithm. 
	   
	   This is based on I-DT of Salvucci and Goldberg (2000).

	   Parameters:
		windowSize: the size of the window (in samples).
		threshold (pixels) the radius in which to consider a fixation.
	"""
	def __init__(self, sampleStream, windowSize, threshold):
		super(Dispersion, self).__init__(sampleStream)
		self.windowSize = windowSize
		self.threshold = threshold
		self.window = []

	def fillWindow(self):
		try:
			while len(self.window) < self.windowSize:
				self.window.append(self.input.next())
		except StopIteration:
			return
	
	def dispersion(self):
		if len(self.window) == 0:
			raise ValueError

		minx = maxx = self.window[0].x
		miny = maxy = self.window[0].y

		for p in self.window:
			minx = min(minx,p.x)
			maxx = max(maxx,p.x)
			miny = min(miny,p.y)
			maxy = max(maxy,p.y)

		return maxx - minx + maxy - miny


	def next(self):
		# Fill the window with samples.
		self.fillWindow()

		if len(self.window) == 0:
			raise StopIteration

		d = self.dispersion()

		if d <= self.threshold:
			# We are in a fixation, but need to grow it
			# until we move above the threshold.

			start = self.window[0]

			while d <= self.threshold:
				try:
					self.window.append(self.input.next())
				except StopIteration:
					break

				d = self.dispersion()
			
				#print ("Window (%f): %s" % (d,str(self.window)))

			end = self.window.pop()
			p = self.centroid(self.window)

			length = len(self.window)
			self.window = []

			return EFixation(p, length, start, end)

		else:
			# Remove the first element
			self.window = self.window[1:]
			# Recurse.
			return self.next()



		

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
import math

class SRR(EventStream):
	"""A velocity and acceleration threshold-based algorithm,
	   based on the descriptions given in the SR Research EyeLink manual (1.3.0)
	   and default parameters given by Holmqvist et al. in 
	   Eye Tracking: A comprehensive guide to methods and measures (2011).
	   
	   The EyeLink algorithm parameters are usually given in terms of
	   degrees/s and degrees/s^2.  Our inputs are consistently based upon
	   pixels/s and pixels/s^2.  The DegreesOfVision class contains translation
	   calculators for converting between these.

	   This algorithm by default does no filtering of input streams.  Use one of the other
	   filter modules to provide custom filtering behaviour prior to applying this event
	   detector.

	   Parameters:
		windowSize: the size of the window (in samples).
		velThresh (pixels/s) The velocity above which to detect a saccade.
		accelThresh (pixels/s^2) The acceleration threshold above which to detect a saccade.
	"""
	def __init__(self, sampleStream, windowSize, velThresh, accelThresh):
		super(SRR, self).__init__(sampleStream)
		self.windowSize = windowSize
		self.velThresh = velThresh
		self.accelThresh = accelThresh
		self.window = []
		self.prevVelocity = 0.0
		self.prevTime = 0

	def fillWindow(self):
		try:
			while len(self.window) < self.windowSize:
				self.window.append(self.input.next())
		except StopIteration:
			return

	def windowVelocity(self):
		""" Compute average inter-sample velocity over a window of samples. """
		prev = self.window[0]

		dsum = 0
		interval = 0

		for curr in self.window[1:]:

			dx = curr.x - prev.x
			dy = curr.y - prev.y
			dt = curr.time - prev.time

			dsum = dsum + math.sqrt(dx * dx + dy * dy)
			interval = interval + dt

		if interval == 0:
			interval = 1

		return dsum / float(interval)

	def windowAccel(self):
		""" Compute instantaneous acceleration over a window of samples. """
		# We use the self.prevVelocity

		currTime = self.window[0].time 
		currVelocity = self.windowVelocity()
		dt = currTime - self.prevTime
		dv = currVelocity - self.prevVelocity

		self.prevVelocity = currVelocity
		self.prevTime = currTime

		if dt == 0.0:
			dt = 1.0

		return dv / dt


	def next(self):
		# Fill the window with samples.
		self.fillWindow()

		if len(self.window) == 0:
			raise StopIteration

		ac = self.windowAccel()
		vc = self.windowVelocity()

		self.window = self.window[1:]

		print "AC: " + str(ac) + " V: " + str(vc)

		return 0


		


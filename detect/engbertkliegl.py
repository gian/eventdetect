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
from eventstream import ESaccade

import math
import random
import numpy as np

class EngbertKliegl(EventStream):
	"""
	   The velocity-based detector of Engbert and Kliegl (2003).
	   This uses the standard deviation of velocity components
	   to detect saccade onsets, with a median estimator.
	   
	   It requires a number of parameters,
	   the values for which will need to be calibrated for a given
	   application and data collection setup.

	   This version of the algorithm does not include the extensions for the use of
	   binocular data --- this would be a possible adaptation, but the current version
	   does not support it because it would render this implementation useless for
	   monocular data without more careful consideration.

	   Parameters:
	     threshold (float) the detection threshold is computed as threshold (lambda) * the median noise level.

	"""
	def __init__(self, sampleStream, threshold):
		super(EngbertKliegl, self).__init__(sampleStream)
		self.threshold = threshold
		self.windowSize = 5
		self.window = []
		self.xRes = [] # x-coordinate reservoir
		self.yRes = [] # y-coordinate reservoir
		self.resSize = 50
		self.buf = [] # Buffer for events
		self.inFix = False
		self.inSacc = False
		random.seed()

	def fillWindow(self):
		try:
			while len(self.window) < self.windowSize:
				self.window.append(self.input.next())
		except StopIteration:
			return

	def windowVelocity(self):
		""" Compute average inter-sample velocity over a window of samples. """
		
		# Pad the window if it is under-size
		
		w = self.window[:]

		while len(w) < self.windowSize:
			w.append(self.window[-1])


		xsum = 0
		ysum = 0

		dt = 0

		xsum = w[4].x + w[3].x - w[1].x - w[0].x
		ysum = w[4].y + w[3].y - w[1].y - w[0].y
		dt = w[4].time - w[0].time

		if dt <= 0:
			dt = 1

		w[2].vx = xsum / float(6 * dt)    # average volocity over 6 samples
		w[2].vy = ysum / float(6 * dt)

		return w[2]

	# Estimate a median by a reservoir-sampling method  ???????? isnt' that the mean?
	def median(self, res):
		# return sum(res) / len(res)
		return np.median(res)

	def medianEstimatorX(self,v):
		if len(self.xRes) < self.resSize:
			self.xRes.append(v*v)
		#else:
		#	p = random.randint(0,len(self.xRes)-1)
		#	self.xRes[p] = v*v

		return self.median(self.xRes)
	
	def medianEstimatorY(self,v):
		if len(self.yRes) < self.resSize:
			self.yRes.append(v*v)
		#else:
		#	p = random.randint(0,len(self.yRes)-1)
		#	self.yRes[p] = v*v

		return self.median(self.yRes)

	def next(self):
		self.fillWindow()

		if len(self.window) <= 3:
			raise StopIteration

		v = self.windowVelocity()

		# print "Velocity: " + str(v.vx) + " / " + str(v.vy)

		mx = self.medianEstimatorX(v.vx)
		my = self.medianEstimatorY(v.vy)
		
		# print "Median: " + str(mx) + " / " + str(my)

		# sdx = (v.vx * v.vx) - (mx * mx)
		sdx = (v.vx * v.vx) - mx
		# sdy = (v.vy * v.vy) - (my * my)
		sdy = (v.vy * v.vy) - my

		# print "Std.Dev: " + str(sdx * self.threshold) + " / " + str(sdy * self.threshold)

		samp = self.window[2]

		r = None

		print "x"
		print v.vx
		print sdx
		print "y"
		print v.vy
		print sdy
		if v.vx >= sdx * self.threshold and v.vy >= sdy * self.threshold:
			self.inSacc = True

			if self.inFix and len(self.buf) > 1:
				self.inFix = False
				c = self.centroid(self.window)
				r = EFixation(c, len(self.buf), self.buf[0], self.buf[-1])
				self.buf = []

			self.buf.append(samp)
		else:
			self.inFix = True

			if self.inSacc:
				self.inSacc = False
				if len(self.buf) > 3:
					r = ESaccade(len(self.buf), self.buf[0], self.buf[-1])
				self.buf = []

		self.window = self.window[1:]
		
		if r != None:
			return r
		else:
			return self.next()


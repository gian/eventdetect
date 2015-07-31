###############################################################################
# Event Detection Algorithm Suite
# Copyright (C) 2012 Gian Perrone (http://github.com/gian)
#	
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both the copyright notice and this permission notice and warranty
# disclaimer appear in supporting documentation, and that the name of
# the above copyright holders, or their entities, not be used in
# advertising or publicity pertaining to distribution of the software
# without specific, written prior permission.
#
# The above copyright holders disclaim all warranties with regard to
# this software, including all implied warranties of merchantability and
# fitness. In no event shall the above copyright holders be liable for
# any special, indirect or consequential damages or any damages
# whatsoever resulting from loss of use, data or profits, whether in an
# action of contract, negligence or other tortious action, arising out
# of or in connection with the use or performance of this software.
###############################################################################

from . import eventstream
from eventstream import EventStream
from eventstream import EFixation
from eventstream import ESaccade
import math
import numpy as np

class SmeetsHooge(EventStream):
	"""A velocity threshold-based algorithm, based on "Nature of Variability
	   in Saccades" by Smeets and Hooge (2003).
		 
	   This algorithm by default does no filtering of input streams.
	   Use one of the other filter modules to provide custom filtering behaviour 
	   prior to applying this event detector.  This is particularly important
	   owing to the use of peak velocity as a measure in this algorithm.
	   The use of a parabolic curve-fitting filter is suggested in the original
	   paper, specifically fitting through groups of 3 subsequent points to
	   estimate the velocity at sample n.

	   The baseline window is defined by two parameters:
	     * How far in the past to start the window before saccade onset.
	     * How many samples to use.

	   For example, if the velocity threshold is crossed at sample t,
	   we would need to seek back to sample t - (n + m) samples to find the
	   start of the sampling window, and then take the average of the samples in
	   the range t - (n + m) ... (t - n) as the baseline velocity with which to
	   calculate saccade onset and offset (the saccade onset is when it reaches
	   3 standard deviations beyond this mean).

	   Note that this algorithm is completely offline.  It needs to be able to
	   seek forward and back arbitrary amounts, therefore it is implemented
	   as a single buffered pass over the input stream.  An online variant
	   is possible, but it is not implemented here for simplicity.

	   Parameters:
		velThresh (pixels/s) The velocity above which to mark a possible saccade.
		windowOffset: The number of samples before the threshold crossing to sample.
		windowSize: the size of the baseline window (in samples).
	"""
	def __init__(self, sampleStream, velThresh, windowSize, windowOffset):
		super(SmeetsHooge, self).__init__(sampleStream)
		self.windowSize = windowSize
		self.velThresh = velThresh
		self.windowOffset = windowOffset
		self.window = []
		self.velocities = dict()
		self.marker = dict()
		self.events = []
		self.exhausted = False

	def fillWindow(self):
		try:
			while True:
				self.window.append(self.input.next())
		except StopIteration:
			return

	def markVelocity(self):
		if len(self.window) == 0:
			return

		""" Marks the set of samples with eventType tags based on velocity. """
		prev = self.window[0]

		dsum = 0
		interval = 0

		self.velocities[0] = 0.0
		self.marker[0] = 0

		for i in range(1, len(self.window)):
			curr = self.window[i]

			dx = curr.x - prev.x
			dy = curr.y - prev.y
			dt = curr.time - prev.time

			prev = curr

			d = math.sqrt(dx * dx + dy * dy)

			if dt == 0:
				dt = 1

			v = d / float(dt)

			self.velocities[i] = v

			if v > self.velThresh:
				self.marker[i] = 1
			else:
				self.marker[i] = 0

	def avgVelocity(self, start, end):
		""" Computes average velocity in a range. """
		v_1 = []
		prev = self.window[start]

		vsum = 0
		interval = 0

		for i in range(start + 1, end):
			curr = self.window[i]

			dx = curr.x - prev.x
			dy = curr.y - prev.y
			dt = curr.time - prev.time

			d = math.sqrt(dx * dx + dy * dy)

			prev = curr

			if dt == 0:
				dt = 1

			v = d / float(dt)

			vsum += v
			interval += dt

			v_1.append(v)
		
		SD = np.std(np.array(v_1))  # compute standard deviation of velocity in the window

		if interval == 0:
		  return {'avg':0, 'SD':0}

		avg = vsum / (end-start-1)   
		# seems like average velocity is calculated weird before.... 
		# should either be as wrote here avg = sum(d)/sum(interval), sum(v)/sum(interval) devides interval twice....
		# return vsum / float(interval)

		return {'avg': avg, 'SD': SD}

	def markSegments(self):
		""" Expands a previously-marked set by computing baselines. """
		inSaccade = False

		for i in range(0, len(self.window)):
			if not inSaccade and self.velocities[i] > self.velThresh:
				inSaccade = True
				baseline = 0.0
				# Start of a marked segment
				if i < self.windowSize + self.windowOffset:
					# We don't have enough samples for a baseline
					inSaccade = False
					continue
				else:
					averageVelocity = self.avgVelocity(i - (self.windowSize + self.windowOffset), i - self.windowOffset)
					# baseline = self.avgVelocity(i - (self.windowSize + self.windowOffset), i - self.windowOffset)

					avg = averageVelocity['avg']
					SD = averageVelocity['SD']
				
				# Seek back to the start of the saccade onset
				for j in range(i - self.windowOffset, i):
					if self.velocities[j] >= 3 * SD + avg:
					# if self.velocities[j] >= 3 * baseline:  baseline was the "incorrect" average velocity, according to the paper, the velocity should exceed mean + 3SD

						self.marker[j] = 1

					else:
						self.marker[j] = 0

				# Seek forward to the end of the saccade
				k = i
				while self.marker[k] == 0:
					k += 1
				maxOff = k + self.windowSize
				if maxOff > len(self.window) - 1:
					maxOff = len(self.window) - 1
				for l in range(k, maxOff):
					if self.velocities[l] >= 3 * SD +avg:
						self.marker[l] = 1
					else:
						self.marker[l] = 0
						inSaccade = False
			else:
				continue


	def computeEvents(self):
		inSaccade = False
		event = []
		for i in range(0, len(self.window)):
			if not inSaccade and self.marker[i] == 0:
				event.append(self.window[i])
				continue
			if inSaccade and self.marker[i] == 1:
				event.append(self.window[i])
				continue
			if inSaccade and self.marker[i] == 0:
				inSaccade = False
				if len(event) > 0:
					e = ESaccade(len(event), event[0], event[-1])
					self.events.append(e)
				event = [self.window[i]]
				continue
			if not inSaccade and self.marker[i] == 1:
				inSaccade = True
				if len(event) > 0:
					c = self.centroid(event)
					e = EFixation(c,len(event),event[0],event[-1])
					self.events.append(e)
				event = [self.window[i]]
				continue
		# Whatever is left over
		if not inSaccade and len(event) > 0:
			c = self.centroid(event)
			e = EFixation(c,len(event),event[0],event[-1])
			self.events.append(e)
			return
		if inSaccade and len(event) > 0:
			e = ESaccade(len(event),event[0],event[-1])
			self.events.append(e)
			return


	def next(self):
		if self.exhausted:
			raise StopIteration

		if len(self.events) == 0:
			# We haven't computed events yet
			self.fillWindow()
			self.markVelocity()
			self.markSegments()
			self.computeEvents()
			if len(self.events) == 0:
				self.exhausted = True
				raise StopIteration
			else:
				e = self.events[0]
				self.events = self.events[1:]
				return e
		else:
			e = self.events[0]
			if len(self.events) == 1:
				self.exhausted = True
				return e

			self.events = self.events[1:]
			return e


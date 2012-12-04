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

class HMM(EventStream):
	"""Hidden Markov Model-based detector.

	   This is based on I-HMM of Salvucci and Goldberg (2000).

	   This is primarily an offline algorithm, in that it needs all input
	   available, and then it caches output.

	   Parameters:
	   	* Fixation Observation Probability mean
	   	* Fixation Observation Probability variance
		* Saccade Observation Probability mean
		* Saccade Observation Probability variance
		* P(fix -> fix)
		* P(fix -> sacc)
		* P(sacc -> sacc)
		* P(sacc -> fix)
	"""
	def __init__(self, sampleStream, fOPm, fOPv, sOPm, sOPv, Pff, Pfs, Pss, Psf):
		super(HMM, self).__init__(sampleStream)
		self.prev = self.input.next()
		self.fOPm = fOPm
		self.fOPv = fOPv
		self.sOPm = sOPm
		self.sOPv = sOPv
		self.Pff = math.log(Pff)
		self.Pfs = math.log(Pfs)
		self.Pss = math.log(Pss)
		self.Psf = math.log(Psf)
		self.output = []
		self.exhausted = False

	def normal(self,mu,sigma,x):
		"""Return P(x) for a normal distribution with given mu and sigma"""
		return (1.0 / (sigma * math.sqrt(2.0 * math.pi))) * math.exp(-math.pow(x - mu,2) / (2 * sigma * sigma))

	def intersampleVelocity(self,prev,curr):
		dx = curr.x - prev.x
		dy = curr.y - prev.y
		dt = curr.time - prev.time

		if dt <= 0:
			# We can't work with a zero or negative time interval, so we
			# Return a large junk value here in the hope it will be filtered.
			return 0.0

		d = math.sqrt(dx * dx + dy * dy)

		return d / float(dt)
	
	# The probability of observing o in state s (fix=0,sac=1)
	def emitP(self,s,o):
		if s == 'fix':
			p = self.normal(self.fOPm,self.fOPv,o)
			if p == 0:
				p = 0.0001
			return math.log(p)
		else:
			p = self.normal(self.sOPm,self.sOPv,o)
			if p == 0:
				p = 0.0001
			return math.log(p)

	def transP(self,s1,s2):
		if s1 == 'fix' and s2 == 'fix':
			return self.Pff
		if s1 == 'fix' and s2 == 'sac':
			return self.Pfs
		if s1 == 'sac' and s2 == 'fix':
			return self.Psf
		if s1 == 'sac' and s2 == 'sac':
			return self.Pss

	# Run the Viterbi algorithm to decode the HMM.
	# Takes a list of 'observations' (read: velocities)
	# Original implementation from:
	# http://en.wikipedia.org/wiki/Viterbi_algorithm
	# Heavily modified to use log probabilities.
	def viterbi(self, obs):
		V = [{}]
		path = {}
		states = ('fix','sac')
		start_p = {}
		start_p['fix'] = math.log(0.55)
		start_p['sac'] = math.log(0.45)
	 
		for y in states:
			V[0][y] = start_p[y] + self.emitP(y,obs[0])
			path[y] = [y]
	 
		for t in range(1,len(obs)):
			V.append({})
			newpath = {}
	 
			for y in states:
				(prob, state) = max([(V[t-1][y0] + self.transP(y0,y) + self.emitP(y,obs[t]), y0) for y0 in states])
				V[t][y] = prob
				newpath[y] = path[state] + [y]
	 
			# Don't need to remember the old paths
			path = newpath
	 
		(prob, state) = max([(V[len(obs) - 1][y], y) for y in states])
		return (prob, path[state])


	def next(self):
		if len(self.output) > 0:
			return self.output.pop(0)

		if self.exhausted:
			raise StopIteration

		obs = [] # Observations
		inp = []

		states = ('fix','sacc')

		
		for curr in self.input:
			v = self.intersampleVelocity(self.prev,curr)

			obs.append(v)
			inp.append(self.prev)
			self.prev = curr

		(pr,V) = self.viterbi(obs)

		inFix = True
		event = []

		for i in range(0,len(V)):
			if V[i] == 'fix' and inFix:
				event.append(inp[i])

			elif V[i] == 'sac' and not inFix:
				event.append(inp[i])

			elif V[i] == 'fix' and not inFix:
				e = ESaccade(len(event),event[0],event[len(event)-1])
				self.output.append(e)
				event = [inp[i]]
				inFix = True

			elif V[i] == 'sac' and inFix:
				c = self.centroid(event)
				e = EFixation(c,len(event),event[0],event[len(event)-1])
				self.output.append(e)
				event = [inp[i]]
				inFix = False

		# Remaining samples?
		if len(event) > 0:
			if not inFix:
				e = ESaccade(len(event),event[0],event[len(event)-1])
				self.output.append(e)

			else:
				c = self.centroid(event)
				e = EFixation(c,len(event),event[0],event[len(event)-1])
				self.output.append(e)


		self.exhausted = True
		
		if len(self.output) > 0:
			return self.output.pop(0)
		else:
			raise StopIteration


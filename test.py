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

from detect.sample import Sample
from detect.sample import ListSampleStream

from detect.dispersion import *
from detect.velocity import *
from detect.hmm import *
from detect.prefix import *
from detect.aoi import *
from detect.movingaverage import *
from detect.srr import *

def lineto (x1,y1,x2,y2,offset,samples,timeInterval):
	l = []
	t = (float(timeInterval) / float(samples))
	xv = (x2 - x1) / float(samples)
	yv = (y2 - y1) / float(samples)

	p = Sample(offset,timeInterval * offset,x1,y1)
	l.append(p)

	for i in range(0,samples):
		p = Sample(i+offset,timeInterval * (offset + i), p.x+xv, p.y+yv)
		l.append(p)
	
	return l

def saccto (x1,y1,x2,y2,offset,samples,timeInterval):
	""" Construct a fake saccade-like set of samples.
	
	    We work in polar coordinates, because it's easier.

	    We first compute the average velocity for half the displacement:
	    (i.e., to the mid-point)
	    v = 0.5r / t
	    Then acceleration:
	    a = 2v / t
	    Then we can iterate over the time range:
	    d(i) = (a * i) * interval
	"""
	l = []

	p = Sample(offset,timeInterval * offset,x1,y1)
	l.append(p)

	r = math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
	theta = math.atan2(y2-y1, x2-x1)

	print "R: " + str(r) + " theta: " + str(theta)

	vAve = r / float(samples)

	print "vAve: " + str(vAve)

	a = (2*vAve) / float(samples / 2)

	v = 0
	xo = x1
	yo = y1

	for i in range(1,1 + (samples / 2)):
		v = v + a

		x = v * math.cos(theta)
		y = v * math.sin(theta)
		xo = xo + x
		yo = yo + y

		print "V: " + str(v / timeInterval)
	
		p = Sample(i+offset,timeInterval * (offset + i), xo, yo)
		l.append(p)
	
	# Reverse acceleration direction
	a = -a
	offset = offset + (samples / 2) + 1

	for i in range(0,(samples / 2)-1):
		v = v + a

		x = v * math.cos(theta)
		y = v * math.sin(theta)
		xo = xo + x
		yo = yo + y

		print "V: " + str(v)
		
		p = Sample(i+offset,timeInterval * (offset + i), xo, yo)
		l.append(p)

		
	
	return l


def fixate (x,y,offset,samples,timeInterval):
	l = []

	for i in range(0,samples):
		p = Sample(i+offset,timeInterval * (offset + i), x, y)
		l.append(p)
	
	return l

testPath = fixate(250,250,0,49,0.001)
testPath.extend(saccto(250,250,550,550,50,100,0.001))
testPath.extend(fixate(550,550,151,99,0.001))
testPath.extend(saccto(550,550,350,150,251,99,0.001))
testPath.extend(fixate(350,150,251,49,0.001))

print "============= I-DT test ==============="

stream = ListSampleStream(testPath)
d = Dispersion(stream, 3, 5)

for i in d:
	print i

print "============= I-VT test ==============="
stream = ListSampleStream(testPath)
v = Velocity(stream, 5)

for i in v:
	print i

print "============= I-HMM test ==============="
testPathB = fixate(500,500,0,3,0.001)
testPathB.extend(saccto(500,500,400,400,4,4,0.001))
testPathB.extend(fixate(400,400,9,4,0.001))
testPathB.extend(saccto(400,400,300,300,13,4,0.001))

print " * Test 1:"

stream = ListSampleStream(testPathB)
h = HMM(stream, 0.01, 100.0, 35355.0, 100.0, 0.95, 0.05, 0.95, 0.05)

for i in h:
	print i

print " * Test 2:"

stream = ListSampleStream(testPath)
h2 = HMM(stream, 0.01, 100.0, 4500.0, 100.0, 0.95, 0.05, 0.95, 0.05)

for i in h2:
	print i

#print "============= Prefix test ==============="
#testPathB = fixate(500,500,0,3,0.001)
#testPathB.extend(saccto(500,500,400,400,4,4,0.001))
#testPathB.extend(fixate(400,400,9,4,0.001))
#testPathB.extend(saccto(400,400,300,300,13,4,0.001))
#
#print " * Test 1:"
#
#stream = ListSampleStream(testPathB)
#h = Prefix(stream, 30)
#
#for i in h:
#	print i
#
#print " * Test 2:"
#
#stream = ListSampleStream(testPath)
#h2 = Prefix(stream, 30)
#
#for i in h2:
#	print i

print "============= I-AOI test ==============="
testPathB = fixate(500,500,0,3,0.001)
testPathB.extend(saccto(500,500,400,400,4,4,0.001))
testPathB.extend(fixate(400,400,9,4,0.001))
testPathB.extend(saccto(400,400,300,300,13,4,0.001))

print " * Test 1:"

stream = ListSampleStream(testPathB)
h = AOI(stream, 3, [(490,490,510,510),(390,390,410,410)])

for i in h:
	print i

print "============= MovingAverageFilter test ==============="
testPathB = fixate(500,500,0,4,0.001)
testPathB.extend(saccto(500,500,400,400,5,4,0.001))
testPathB.extend(fixate(400,400,10,4,0.001))
testPathB.extend(saccto(400,400,300,300,14,4,0.001))

print " * Test 1:"

stream = MovingAverageFilter(ListSampleStream(testPathB),3)
h = AOI(stream, 3, [(490,490,510,510),(390,390,410,410)])

for i in h:
	print i

print "============= SRR test ==============="

path = saccto(100,100,500,500,0, 10, 0.001)

for i in path:
	print i



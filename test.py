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

def fixate (x,y,offset,samples,timeInterval):
	l = []

	for i in range(0,samples):
		p = Sample(i+offset,timeInterval * (offset + i), x, y)
		l.append(p)
	
	return l

testPath = fixate(250,250,0,49,0.001)
testPath.extend(lineto(250,250,550,550,50,100,0.001))
testPath.extend(fixate(550,550,151,99,0.001))
testPath.extend(lineto(550,550,350,150,251,99,0.001))
testPath.extend(fixate(350,150,251,49,0.001))

print "============= I-DT test ==============="

stream = ListSampleStream(testPath)
d = Dispersion(stream, 3, 5)

for i in d:
	print i



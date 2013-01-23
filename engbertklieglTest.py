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
from detect.sample import FileSampleStream

from detect.dispersion import *
from detect.velocity import *
from detect.hmm import *
from detect.prefix import *
from detect.aoi import *
from detect.movingaverage import *
from detect.srr import *
from detect.engbertkliegl import *

print "============= EngbertKliegl test ==============="

stream = FileSampleStream('testData/UH27_img_vy_labelled_MN.txt')

d = EngbertKliegl(stream, 6)

fixations = []

for i in d: 
	fixations.append(i)

#verifStream = FileSampleStream('testData/UH27_img_vy_labelled_MN.txt')

#taggedEvents = []
#cfix = []
#eventType = []
#for i in verifStream:
#	if i.eventType == 1:
#		cfix.append(i)
#		eventType.append(1)
#	else:
#		eventType.append(0)
#		if len(cfix) == 0:
#			continue
#		print ("Fixation of length: " + str(len(cfix)) + " starting at sample " + str(cfix[0].index))
#		p = idt.centroid(cfix)
#
#		f = EFixation(p, len(cfix), cfix[0], cfix[-1])
#		taggedEvents.append(f)
#		cfix = []
#
#matchedSamples = 0
#errorSamples = 0
#
##for f in fixations:
##	s = f.start.index
##	for i in range(s,s+f.length):
##		if eventType[i] == 1:
##			matchedSamples = matchedSamples + 1
#		else:
#			errorSamples = errorSamples + 1
#
#mPct = matchedSamples / float(len(eventType))
#ePct = errorSamples / float(len(eventType))
#
#print "Matched Samples: " + str(matchedSamples) + " (" + str(mPct * 100) + "%)"
#print "Error Samples: " + str(errorSamples) + " (" + str(ePct * 100) + "%)"

#

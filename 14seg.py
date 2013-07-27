#!/usr/bin/env python
#
#
#
import math

#
# roughly 90x90 cm windows
#

#  ___
# |\|/|
#  ---
# |/|\|
#  ---
#
# top/bottom: 	1.5
# side: 	3.3
# 

#
# pass in total height
#
def calc_14seg(height):
  height = height / 2.0
  width = height / (4/3.0)
  diag = math.sqrt((height ** 2) + (width ** 2))
  length = (diag * 4) + (width * 6) + (height * 6)
  print "%-3.2f, %-2.2f, %-2.2f, %-2.2f, %-2.2f" % (height, width, diag, length / 100.0, 4000 / length)
  etot = 0
  for t in (height, width, diag):
    e = t % 5.0
    etot += e
    print " %-3.2f," % (e),
  print "%-3.2f" % (etot)

  print
  print "length, number of that length"
  for t in ((height, 6), (width, 6), (diag, 4)):
    s = int(t[0] / 5.0)
    print "%5d, %d" % (s, t[1])

if __name__ == "__main__":
  print "height, width, diag, length, nchar"
#  for i in range(6, 12, 2):
#  	calc_14seg(i * 5.0)
  calc_14seg(40.0)

  
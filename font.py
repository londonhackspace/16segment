#!/usr/bin/env python

import sys, serial, time, random, os
import readline
from sixteensegfont import font

#font = {}

#
# the bit order is different on the hardware due to the order of the
# bits in the shift registers
#
def mangle(c):
    mangled = "{0:04x}".format(c)
#        last nibble -> first
#        first -> last
#        middle 2 swap
#        3210    3210
#        c387 -> 783c
    return "%c%c%c%c" % (mangled[3], mangled[2], mangled[1], mangled[0])

#  _ _
# |\|/|
#  - -
# |/|\|
#  - -
def set(bit, char):
  if bit:
    return char
  else:
    return " "

#  
#   a b
#   _ _

#  cdefg
#  |\|/|

#   h i
#   - -

#  jklmn
#  |/|\|

#   o p
#   - -
def seg_char(bits):
  # abcd efgh ijkl mnop
  # 0123 4567 8911 1111
  #             01 2345
  o = " "
  o += set(bits & 1, "_")
  o += " "
  o += set(bits & (1 << 1), "_")
  print o

  o = ""
  o += set(bits & (1 << 2), "|")
  o += set(bits & (1 << 3), "\\")
  o += set(bits & (1 << 4), "|")
  o += set(bits & (1 << 5), "/")
  o += set(bits & (1 << 6), "|")
  print o
  
  o = ""
  o += " "
  o += set(bits & (1 << 7), "-")
  o += " "
  o += set(bits & (1 << 8), "-")
  print o

  o = ""
  o += set(bits & (1 << 9), "|")
  o += set(bits & (1 << 10), "/")
  o += set(bits & (1 << 11), "|")
  o += set(bits & (1 << 12), "\\")
  o += set(bits & (1 << 13), "|")
  print o

  o = ""
  o += " "
  o += set(bits & (1 << 14), "-")
  o += " "
  o += set(bits & (1 << 15), "-")
  print o    

def dump_arduino(font):
    ks = font.keys()
    ks.sort()
    
    print "#include <avr/io.h>"
    print "#include <avr/pgmspace.h>"
    print
    print "static uint16_t font[] PROGMEM = {"
    
    for k in [chr(c) for c in range(ord(' '), 127)]:
        print "\t0b{0:016b}, // {1:s} - {0:04x} - {3:s}".format(font[k], k, font[k], mangle(font[k]))
    
    print "};"

def dump_python(font):
    # broken, needs to escape ' & \
    ks = font.keys()
    ks.sort()
    
    print "#!/usr/bin/env python"
    print
    print "font = {"
    
    for k in [chr(c) for c in range(ord(' '), 127)]:
        print "\t'{1:s}': 0x{0:04x}, # {0:04x} - 0b{0:016b}".format(font[k], k, font[k], mangle(font[k]))
    
    print "}"
    
if __name__ == "__main__":
    for file in sys.argv[1:]:
        f = open(file, 'r')
        for l in f:
            try:
                bin, k = l.strip().split(' ')
            except:
                bin = l.strip().split(' ')[0]
                k = ' '
            font[k] = int(bin, 2)
        f.close()

    dev = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_74137363737351B0F0D1-if00"
    if os.path.exists(dev):
        s = serial.Serial(dev, 9600)
    else:
        class NotSerial:
            def write(self, text):
                print text

            def inWaiting(self):
                return 0
            
            def read(self):
                return
                
        s = NotSerial()

    def message(str):
        for c in str:
            seg_char(font[c])
            s.write("w" + mangle(font[c]))
            time.sleep(0.5)

    def clear():
        s.write("r")
        time.sleep(0.2)

    def all():
        for i in range(0,8):
            s.write("wffff")
            time.sleep(0.2)

    clear()

    def info():
        print "'quit' to quit"
        print "'rhhhh' or 'rbbbbbbbbbbbbbbbb' to write a raw char in hex or binary"
        print "'wstring' to display text"
        print "'a' to print all chars"
        print "'b' to cycle through all bits"
        print "'c' to clear the display"
    
    info()
    readline.parse_and_bind('tab: complete')
    while True:
        line = raw_input('> ')
        line = line.strip()
        if line == 'quit':
            exit(0)
        elif line.startswith('w'):
            message(line[1:])
        elif line.startswith('r'):
            line = line.replace(' ', '')
            line = line[1:]
            if len(line) == len('ffff'):
                c = int(line,16)
            elif len(line) == len('0000111100001111'):
                c = int(line,2)
            print "%04x" % (c)
            seg_char(c)
            s.write("w" + mangle(c))
        elif line.startswith('a'):
            for c in [chr(c) for c in range(ord(' '), 127)]:
                seg_char(font[c])
                s.write("w" + mangle(font[c]))
                time.sleep(0.75)
        elif line.startswith('b'):
            for i in range (0,16):
                print i
                for j in range(0,7):
                    o = "w" + mangle(1 << i)
                    print o
                    s.write(o)
                    time.sleep(0.01)
                    if s.inWaiting() > 0:
                        print s.read()
                time.sleep(0.2)
        elif line.startswith('c'):
            clear()
        elif line.startswith('h') or line.startswith('?'):
            info()

    exit(0)
            
#            s.write("w" + "%04x" % (int(random.random() * 65535)))
#            time.sleep(0.1)

#    while True:
#        line = raw_input("String>  ")
#        if line == "":
#            sys.exit(0)
#        if(line == "..."):
#            print_all_chars()
#        else:
#            print_ascii_as_16seg(line)
#        sys.stdout.write("\n")




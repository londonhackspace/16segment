#!/usr/bin/env python
import sys, serial, time, random

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

# Turns "abcjgnhi" into int for segment activation
def str2bits(s):
    bits = 0
    for c in s:
        if ord(c) < 97 or ord(c) > 112: # a-p
            raise("Letters a-p only")
        bits = bits | (1 << (ord(c)-97))
    return bits

def set(bit, char):
    if bit:
        return char
    else:
        return " "

## Creates list of 5 lists - one per row when rendering charater in ascii
def bits_to_rows(bits):
    return [
        [" ", set(bits & 1, "_"), " ", set(bits & (1 << 1), "_"), " "],
        [set(bits & (1 << 2), "|"), set(bits & (1 << 3), "\\"), set(bits & (1 << 4), "|"), set(bits & (1 << 5), "/"), set(bits & (1 << 6), "|")],
        [" ", set(bits & (1 << 7), "-"), " ", set(bits & (1 << 8), "-"), " "],
        [set(bits & (1 << 9), "|"), set(bits & (1 << 10), "/"), set(bits & (1 << 11), "|"), set(bits & (1 << 12), "\\"), set(bits & (1 << 13), "|")],
        [" ", set(bits & (1 << 14), "-"), " ", set(bits & (1 << 15), "-"), " "]
    ]

fontmap = {
    ' ': 0x0,
#    '@': "abcdefghijklmnop",
    '$': "abchinopel",
    '&': "ehil", # +
    '\'': "e",
    '*': "defhiklm",
    '+': "ehil",
    '-': "hi",
    '/': "kf",
    '0': "abgnpojckf",
    '1': "aelop",
    '2': "abghijop",
    '3': "abhiopgn",
    '4': "chign",
    '5': "abchinop",
    '6': "abchijnop",
    '7': "abfk",
    '8': "ancghijnop",
    '9': "abcghinop",
    '<': "fm",
    '>': "dk",
    '?': "abgil",
    'A': "abcghijn",
    'B': "abgnopeli",
    'C': "bacjop",
    'D': "abgnopel",
    'E': "abcjophi",
    'F': "abcjhi",
    'G': "abcjopni",
    'H': "cjgnhi",
    'I': "abopel",
    'J': "bgnpoj",
    'K': "cjhfm",
    'L': "cjop",
    'M': "cdfgjn",
    'N': "jcdmng",
    'O': "abcgjnop",
    'P': "cjhigab",
    'Q': "abgnpojcm",
    'R': "jcabgihm",
    'S': "bachinpo",
    'T': "abel",
    'U': "cjopng",
    'V': "cjkf",
    'W': "cjopngl",
    'X': "dfkm",
    'Y': "dfl",
    'Z': "abfkop",
    '[': "acjo",
    '\\': "dm",
    ']': "bgnp",
    '^': "km",
    '_': "op",
    '`': "d",
    '|': "el",
}

def generate_font(fontmap):
    font = {}
    for k in fontmap:
        if isinstance(fontmap[k], int):
            font[k] = fontmap[k]
        else:
            font[k] = str2bits(fontmap[k])
    return font

font = generate_font(fontmap)

def print_ascii_as_16seg(s):
    codes = str_to_codes(s)
    print_asciiart_from_codes(codes)
    print s + " --> ",
    for c in codes:
        print c,
    sys.stdout.write("\n")

def str_to_codes(s):
    codes = []
    for char in s:
        if not char in font:
            fontcode = 0xffff
        else:
            fontcode = font[char]
        codes.append(fontcode)
    return codes

def print_asciiart_from_codes(codes):
    rowchars = [bits_to_rows(fontcode) for fontcode in codes]
    # Print!
    for rownum in range(0,5):
        for character in rowchars:
            for char in character[rownum]:
                sys.stdout.write(char)
            sys.stdout.write(" ") # end of character column spacing
        sys.stdout.write("\n")

def print_all_chars():
    i = 0
    tmp = ""
    for k in sorted(font):
        tmp = tmp + k
        i = i + 1
        if(i % 10 == 0):
            print_ascii_as_16seg(tmp)
            sys.stdout.write("\n")
            tmp = ""
            i = 0

def mangle(c):
    mangled = "{0:04x}".format(c)
#        last nibble -> first
#        first -> last
#        middle 2 swap
#        3210    3210
#        c387 -> 783c
    return "%c%c%c%c" % (mangled[3], mangled[2], mangled[1], mangled[0])
    

if __name__ == "__main__":

    font['!'] = 0b0000100000010000
    font['"'] = 0b0000000000010100
    font['#'] = 0b0010100111010011
#    font['%'] = 
    font['('] = 0b0001000010100000
    font[')'] = 0b0000010100001000
    font[','] = 0b0000010000000000
    font['.'] = 0b0100000000000000
    font[':'] = 0b0000100000010000
    font[';'] = 0b0000010000010000
    font['='] = 0b1000000100000000
    
    ks = font.keys()
    ks.sort()
    
#    print "#include <avr/io.h>"
#    print "#include <avr/pgmspace.h>"
#    print
#    print "static uint16_t font[] PROGMEM = {"
    
    for k in ks:
#        print "\t0b{0:016b}, // {1:s} - {0:04x} - {3:s}".format(font[k], k, font[k], mangle(font[k]))
        print "0b{0:016b} {1:s}".format(font[k], k, mangle(font[k]))
    
#    print "};"

    exit(0)

    dev = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_74137363737351B0F0D1-if00"
    
    s = serial.Serial(dev, 9600)

    def message(str):
        for c in str:
            s.write("w" + mangle(font[c.upper()]))
            time.sleep(0.5)

    def clear():
        for i in range(0,8):
            s.write("r")
            time.sleep(0.2)
        time.sleep(0.2)

    def all():
        for i in range(0,8):
            s.write("wffff")
            time.sleep(0.2)

    clear()
    while 1:
        message("Hello John :) Welcome to London Hackspace")

    exit(0)

    while 1:
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

    exit(0)
        
    clear()
    time.sleep(10)
    all()
    time.sleep(10)
    clear()
    time.sleep(2)
    s.flush()
    exit(0)
    
    stime = time.time()
    state = 'e'
    while True:
        if state == 'e':
            emfcamp()
        else:
            s.write("w" + "%04x" % (int(random.random() * 65535)))
            time.sleep(0.1)
        if (time.time() - stime ) > 5:
            stime = time.time()
            if state == 'e':
                state = 'r'
            else:
                state = 'e'

#    while True:
#        line = raw_input("String>  ")
#        if line == "":
#            sys.exit(0)
#        if(line == "..."):
#            print_all_chars()
#        else:
#            print_ascii_as_16seg(line)
#        sys.stdout.write("\n")




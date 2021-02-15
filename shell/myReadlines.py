#! /usr/bin/env python3

import os, sys, time, re

ibuf = ""      # input buffer
sbuf = ""      # string buffer
sbufLength = 0 # string buffer length
currChar = 0   # index of current char in string buffer

def getChar():
    global ibuf
    global sbuf
    global sbufLength
    global currChar

    if currChar == sbufLength: # if reached end of string buffer get a new line and reset values
        ibuf = os.read(0, 100)
        sbuf = ibuf.decode()
        sbufLength = len(sbuf)
        currChar = 0
        if sbufLength == 0:    # if reached the end of the input return nothing
            return ''

    char = sbuf[currChar]
    currChar += 1
    return char

def myReadlines():
    char = getChar()
    line = ""

    while char != '\n':        # keep getting chars for line until new line
        line += char
        char = getChar()
        if char == '':         # if char is empty then we reached end of file
            return line
    line+= '\n'                # if new line is found return the line with a new line char
    return line

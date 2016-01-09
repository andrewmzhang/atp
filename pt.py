#!/usr/bin/python

from atp import *
import Image, sys

path = sys.argv[1]
pic = Image.open(path)

printer = atp()
printer.printImage(pic, True)
printer.feedClear()

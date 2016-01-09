#!/usr/bin/python

from atp import *
import Image, ImageDraw, sys

path = sys.argv[1]
pic = Image.open(path)

# resize pic to fit 384 if wider
if pic.size[0] > 384:
	newsize = (384, int(pic.size[1] / (pic.size[0] / 384.0)))
	pic = pic.resize(newsize, Image.ANTIALIAS)

printer = atp()
printer.printImage(pic, True)
printer.feedClear()

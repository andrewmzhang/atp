#!/usr/bin/python

from atp import *
import sys, textwrap, os, unidecode

ebook_path = sys.argv[1]
title = os.path.basename(os.path.splitext(ebook_path)[0])

p = atp()

# Title from filename
p.justify(p.CENTER)
p.setSize(p.TALL)
p.println(title)

# Reset style for body
p.justify()
p.setSize(p.TINY)
p.feed(1)

# Print each line. Approximate unicode characters in ASCII
# and wrap text neatly on word breaks to fit column width.
with open(ebook_path, 'r') as f:
	for line in f:
		line = unidecode.unidecode(line.decode('utf_8'))
		text = textwrap.fill(line, p.maxColumn)
		p.write(text, '\n')

p.feedClear()

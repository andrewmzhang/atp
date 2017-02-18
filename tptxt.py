#!/usr/bin/python

from unidecode import unidecode
from textwrap import wrap
import sys

class TPJob():
	
	# font metrics.
	# 'name': [row height, characters per line]
	# row height = font height + associated default line spacing
	metrics = {
			'tall':   [56, 32],
			'medium': [32, 32],
			'small':  [21, 42]
	}
	
	# rows to feed to clear the serrated cutter when print done
	feedRows = 64
	
	# mm height of each row according to available documentation
	# actual value may be very slightly higher
	mmPerRow = 0.125
	
	# these lists hold the lines that comprise each of those sections
	titleLines = []
	subtitleLines = []
	textLines = []
	
	def __init__(self, lines, header=False, title=None, subtitle=None):
		
		lineIndex = 0
		
		if header == True:
		
			# loop through lines until first blank, appending everything to titleLines
			for line in lines:
				lineIndex += 1
				if line == '':
					break
				self.titleLines.append(line)
			
			for line in lines[lineIndex:]:
				lineIndex += 1
				if line == '':
					break
				# increment line index after break from subtitle
				# to include the following blank line in text.
				self.subtitleLines.append(line)
		
		if title:
			self.titleLines = title
		
		if subtitle:
			self.subtitleLines = subtitle
		
		self.textLines = lines[lineIndex:]
		
	def dump(self, outputFile=None):
		
		if len(self.titleLines) > 0:
			for line in self.titleLines:
				print >> outputFile, line
			print >> outputFile
		
		if len(self.subtitleLines) > 0:
			for line in self.subtitleLines:
				print >> outputFile, line
			print >> outputFile
			
		for line in self.textLines:
			print >> outputFile, line
	
	def reformat(self, size='small'):
		self.reformatTitle()
		self.reformatSubtitle()
		self.reformatText(size)
	
	def reformatTitle(self):
		newTitleLines = []
		for titleLine in self.titleLines:
			newTitleLines.extend(wrap(unidecode(titleLine.decode('utf_8')), self.metrics['tall'][1]))
		self.titleLines = newTitleLines
	
	def reformatSubtitle(self):
		newSubtitleLines = []
		for subtitleLine in self.subtitleLines:
			newSubtitleLines.extend(wrap(unidecode(subtitleLine.decode('utf_8')), self.metrics['medium'][1]))
		self.subtitleLines = newSubtitleLines
	
	def reformatText(self, size):
		
		# Try treating consecutive lines that are not blank as part of the same
		# line (joined by a space). Blank lines ([] or '') denote true new lines.
		# So, first concatenate runs of non-blank lines, inserting spaces if needed,
		# *then* wrap them, and append the wrapped concatenation to the output lines.
		
		newTextLines = []
		for textLine in self.textLines:
			tl = wrap(unidecode(textLine.decode('utf_8')), self.metrics[size][1])
			if tl == []:
				tl = ['']
			newTextLines.extend(tl)
		self.textLines = newTextLines
	
	def estimate(self, size='small'):
		totalTapeLength = self.titleTapeLength()
		totalTapeLength += self.subtitleTapeLength()
		
		# whitespace row between title/subtitle (if present) and text
		if totalTapeLength > 0:
			totalTapeLength += self.tapeLength(1, self.metrics[size][0])
		
		totalTapeLength += self.textTapeLength(size)
		totalTapeLength += self.feedTapeLength()
		
		# 2.5 fudge for agreement with actual length of a particular test case
		# repeat tests with files of varying length and adjust mmPerRow to resolve
		return totalTapeLength + 2.5
	
	def tapeLength(self, lineCount, rowsPerLine):
		return lineCount * rowsPerLine * self.mmPerRow
		
	def titleTapeLength(self):
		return self.tapeLength(len(self.titleLines), self.metrics['tall'][0])
	
	def subtitleTapeLength(self):
		return self.tapeLength(len(self.subtitleLines), self.metrics['medium'][0])
	
	def textTapeLength(self, size):
		return self.tapeLength(len(self.textLines), self.metrics[size][0])
	
	def feedTapeLength(self):
		return self.tapeLength(1, self.feedRows)
	
	def send(self, size='small'):
		
		from atp import atp
		p = atp(timeout=5)
		
		nt = len(self.titleLines)
		ns = len(self.subtitleLines)
		
		# display a progress bar to be updated as each line is printed
		# also useful for assessing serial speed/sync - which finishes first?
		steps = nt + ns + len(self.textLines)
		progress = Progressbar(steps)
		
		# title and subtitle are centered
		if nt > 0 or ns > 0:
			p.justify(p.CENTER)
		
		# title is tall font
		if nt > 0:
			p.setSize(p.TALL)
			for t in self.titleLines:
				p.write(t, '\n')
				progress.update()
		
		# subtitle is normal font
		if ns > 0:
			p.setSize(p.NORMAL)
			for t in self.subtitleLines:
				p.write(t, '\n')
				progress.update()
		
		# body text is left justified
		# body font is user selected
		p.justify(p.LEFT)
		p.setSize({'tall': p.TALL, 'medium': p.NORMAL, 'small': p.TINY}[size])
		
		# insert one row of text height whitespace after title/subtitle 
		if nt > 0 or ns > 0:
			p.feed(1)
		
		for t in self.textLines:
			if t == "*" or t == "***":
				# horizontal rule hack
				p.justify(p.CENTER)
				p.writeBytes(0xC4, 0xC4, 0xC4)
				p.write('\n')
				p.justify(p.LEFT)
			elif t.find('^') == 0:
				p.justify(p.CENTER)
				p.write(t[1:], '\n')
				p.justify(p.LEFT)
			else:
				p.write(t, '\n')
			progress.update()
		
		p.feedRows(self.feedRows)
		p.close()
		progress.done()

class Progressbar():
	
	def __init__(self, steps, size=20):
		self.size = size
		self.reset(steps)
	
	def reset(self, steps):
		self.total = steps
		self.current = 0
	
	# http://stackoverflow.com/a/15860757
	def update_display(self, progress):
		status = ""

		if progress < 0:
			progress = 0
			status = "Halt.\r\n"
		
		if progress >= 1:
			progress = 1
			status = "Done.\r\n"
		
		block = int(round(self.size * progress))
		text = "\rPercent: [{0}] {1}% {2}".format(
				"#" * block + "-" * (self.size - block),
				int(progress * 100),
				status)
		
		sys.stdout.write(text)
		sys.stdout.flush()
	
	def update(self):
		self.update_display(float(self.current)/self.total)
		self.current += 1
	
	def halt(self):
		self.reset(self.total)
		self.update_display(0)
	
	def done(self):
		self.current = self.total
		self.update_display(1)

def main():

	from argparse import ArgumentParser, FileType
	
	# argparse option validators
	def positive_integer(string):
		value = int(string)
		if value <= 0:
			msg = "%r is not a positive integer" % string
			raise argparse.ArgumentTypeError(msg)
		return value
	
	ap = ArgumentParser(description='Prepare a text file for receipt printer.')
	ap.add_argument('--verbatim', action='store_true', default=False,
			help='Assume input text is pre-formatted.')
	ap.add_argument('--dump', default=None, type=FileType('w'), metavar='PATH',
			help='Write formatted text to PATH (- for stdout).')
	ap.add_argument('--print', dest='toast', action='store_true', default=False,
			help='Send output to printer.')
	ap.add_argument('--copies', type=positive_integer, action='store', default=1, metavar='N',
			help='Print N copies.')
	ap.add_argument('--limit', type=float, action='store', default=None, metavar='MAX',
			help='Send output to printer only if total estimated length < MAX.')
	ap.add_argument('--size', action='store', choices=['small', 'medium'], default='small',
			help='Body font size.')
	ap.add_argument('--header', action='store_true', default=False,
			help='Text begins with title and subtitle header lines.')
	ap.add_argument('--title', action='append', default=None,
			help='Text title. Overrides title from header if present.')
	ap.add_argument('--subtitle', action='append', default=None,
			help='Text subtitle. Overrides subtitle from header if present.')
	ap.add_argument('INPUT', action='store', nargs='?', type=FileType('r'), default=sys.stdin,
			help='Input text file.')
	args = ap.parse_args()
	
	# 1. Read the textfile, stripping trailing newlines/whitespace.
	job= TPJob([line.rstrip() for line in args.INPUT], header=args.header, title=args.title, subtitle=args.subtitle)
	args.INPUT.close()
	
	# 2. Reformat unless instructed to use input as-is. (Preformatted? Maybe needless.)
	#    Reformatting entails Unicode-to-ASCII transliteration and word wrapping.
	if not args.verbatim:
		job.reformat(args.size)
	
	# 3. Calculate and report estimated paper length.
	length = job.estimate(args.size)
	print "Estimated document length: {mm:.0f} mm ({inch:.1f} inches or {foot:.2f} feet)".format(
		mm=length, inch=length / 25.4, foot=length / 304.8)
	if args.copies > 1:
		length *= args.copies
		print "Total length for {n:d} copies: {mm:.0f} mm ({inch:.1f} inches or {foot:.2f} feet)".format(
			n=args.copies, mm=length, inch=length / 25.4, foot=length / 304.8)
	
	# 4. Output the reformatted text if requested.
	if args.dump != None:
		job.dump(args.dump)
	
	# 5. Print the text only if instructed. If a length limit is specified,
	#    do not print if the estimated length exceeds the specified maximum.
	if (args.limit == None and args.toast) or (args.limit != None and length <= args.limit):
		for i in range(args.copies):
			job.send(args.size)
	else:
		if args.limit != None:
			print "Estimated length exceeds limit of {mm:.0f} mm.".format(mm=args.limit)

if __name__ == "__main__":
	main()

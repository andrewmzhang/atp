#!/usr/bin/python

from unidecode import unidecode
from textwrap import wrap
import sys

class TPJob():
	
	# fixed metrics for each section's font
	titleWrapWidth = 32
	titleFontHeight = 48
	titleLineSpacing = 8
	titleLineHeight = titleFontHeight + titleLineSpacing
	creditWrapWidth = 32
	creditFontHeight = 24
	creditLineSpacing = 8
	creditLineHeight = creditFontHeight + creditLineSpacing
	textWrapWidth = 42
	textFontHeight = 17
	textLineSpacing = 4
	textLineHeight = textFontHeight + textLineSpacing
	
	# rows to feed to clear the serrated cutter when print done
	feedRows = 64
	
	# mm height of each row according to available documentation
	# actual value may be very slightly higher
	mmPerRow = 0.125
	
	# each file is comprised of a title, credit byline, and text body
	# these lists hold the lines that comprise each of those sections
	titleLines = []
	creditLines = []
	textLines = []
	
	def __init__(self, lines):
		
		lineIndex = 0
		
		# loop through lines until first blank, appending everything to titleLines
		for line in lines:
			lineIndex += 1
			if line == '':
				break
			self.titleLines.append(line)
		
		for line in lines[lineIndex:]:
			if line == '':
				break
			# increment line index after break from credit
			# to include the following blank line in text.
			lineIndex += 1
			self.creditLines.append(line)
		
		self.textLines = lines[lineIndex:]
		
	def dump(self, outputFile=None):
		
		for line in self.titleLines:
			print >> outputFile, line
		print >> outputFile
		
		for line in self.creditLines:
			print >> outputFile, line
		# treating blank line after credit as first line of text
		#print >> outputFile
		
		for line in self.textLines:
			print >> outputFile, line
	
	def reformat(self):
		self.reformatTitle()
		self.reformatCredit()
		self.reformatText()
	
	def reformatTitle(self):
		newTitleLines = []
		for titleLine in self.titleLines:
			newTitleLines.extend(wrap(unidecode(titleLine.decode('utf_8')), self.titleWrapWidth))
		self.titleLines = newTitleLines
	
	def reformatCredit(self):
		newCreditLines = []
		for creditLine in self.creditLines:
			newCreditLines.extend(wrap(unidecode(creditLine.decode('utf_8')), self.creditWrapWidth))
		self.creditLines = newCreditLines
	
	def reformatText(self):
		# todo: consecutive text lines should 
		newTextLines = []
		for textLine in self.textLines:
			tl = wrap(unidecode(textLine.decode('utf_8')), self.textWrapWidth)
			if tl == []:
				tl = ['']
			newTextLines.extend(tl)
		self.textLines = newTextLines
	
	def estimate(self):
		totalTapeLength = self.titleTapeLength()
		totalTapeLength += self.creditTapeLength()
		totalTapeLength += self.textTapeLength()
		totalTapeLength += self.feedTapeLength()
		# 2.5 fudge for agreement with actual length of a particular test case
		# repeat tests with files of varying length and adjust mmPerRow to resolve
		return totalTapeLength + 2.5
	
	def tapeLength(self, lineCount, rowsPerLine):
		return lineCount * rowsPerLine * self.mmPerRow
		
	def titleTapeLength(self):
		return self.tapeLength(len(self.titleLines), self.titleLineHeight)
	
	def creditTapeLength(self):
		return self.tapeLength(len(self.creditLines), self.creditLineHeight)
	
	def textTapeLength(self):
		return self.tapeLength(len(self.textLines), self.textLineHeight)
	
	def feedTapeLength(self):
		return self.tapeLength(1, self.feedRows)
	
	def send(self):
		
		from atp import atp
		p = atp(timeout=5)
		
		# display a progress bar to be updated as each line is printed
		# also useful for assessing serial speed/sync - which finishes first?
		steps = len(self.titleLines) + len(self.creditLines) + len(self.textLines)
		progress = Progressbar(steps)
		
		# title and credit are centered
		p.justify(p.CENTER)
		
		# title is tall font
		p.setSize(p.TALL)
		for t in self.titleLines:
			p.write(t, '\n')
			progress.update()
		
		# credit is normal font
		p.setSize(p.NORMAL)
		for t in self.creditLines:
			p.write(t, '\n')
			progress.update()
		
		# body text is tiny font
		p.justify(p.LEFT)
		p.setSize(p.TINY)
		for t in self.textLines:
			if t == "*" or t == "***":
				# horizontal rule hack
				p.justify(p.CENTER)
				p.writeBytes(0xC4, 0xC4, 0xC4)
				p.write('\n')
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

	from argparse import ArgumentParser

	ap = ArgumentParser(description='Prepare a text file for receipt printer.')
	ap.add_argument('--verbatim', action='store_true', default=False,
			help='Assume input text is pre-formatted.')
	ap.add_argument('--save', action='store', default=None, metavar='PATH',
			help='Write formatted text to FILE.')
	ap.add_argument('--dump', action='store_true', default=False,
			help='Write formatted text to stdout.')
	ap.add_argument('--print', dest='toast', action='store_true', default=False,
			help='Send output to printer.')
	ap.add_argument('--limit', type=float, action='store', default=None, metavar='MAX',
			help='Send output to printer only if estimated length < MAX.')
	ap.add_argument('INPUT', action='store',
			help='Path to input text file.')
	args = ap.parse_args()
	
	# 1. Read the textfile. Title and credit lines assumed present but may be unwrapped.
	with open(args.INPUT, 'r') as inputFile:
		# readlines without trailing newline/whitespace
		job= TPJob([line.rstrip() for line in inputFile])
	
	# 2. Reformat unless instructed to use input as-is. (Preformatted? Maybe needless.)
	#    Reformatting entails Unicode-to-ASCII transliteration and word wrapping.
	if not args.verbatim:
		job.reformat()
	
	# 3. Calculate and report estimated paper length.
	length = job.estimate()
	print "Estimate: {mm:.0f} mm ({inch:.1f} inches or {foot:.2f} feet)".format(
		mm=length, inch=length / 25.4, foot=length / 304.8)
	
	# 4. Output the reformatted text to file or stdout if requested.
	if args.save != None:
		with open(args.save, 'w') as outputFile:
			job.dump(outputFile)
	if args.dump:
		job.dump()
	
	# 5. Print the text only if instructed. If a length limit is specified,
	#    do not print if the estimated length exceeds the specified maximum.
	if (args.limit == None and args.toast) or (args.limit != None and length <= args.limit):
		job.send()
	else:
		if args.limit != None:
			print "Estimated length exceeds limit of {mm:.0f} mm.".format(mm=args.limit)

if __name__ == "__main__":
	main()

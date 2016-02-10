#!/usr/bin/python

import mistune
import sys

class ATPRenderer(mistune.Renderer):
	
	def placeholder(self):
		return []
	
	# Block level
	
	def block_code(self, code, language=None):
		return ['%s' % code]
	
	def block_quote(self, text):
		return ['%s' % text]
	
	def block_html(self, html):
		return ['%s' % html]
		
	def header(self, text, level, raw=None):
		# select font based on header level
		return [
			'\n',
			# setsize large
			[27, 33, 48],
			[27, 51, 56],
			# inverse text
			[29, 66, 1],
			'%s' % text[0],
			[29, 66, 0],
			# setsize normal
			[27, 33, 0],
			[27, 51, 32],
			'\n'
		]
	
	def hrule(self):
		return []
	
	def list(self, body, ordered=True):
		return ['%s' % body]
		
	def list_item(self, text):
		return ['%s' % text]
	
	"""
	textwrapping to maxcharwidth of the font size is desired.
	again, may require subclassing mistune to get the wrapping
	applied at the right phase, since we don't need/want to
	count the raw markdown markup characters in line width,
	and the text received here may already be split into span
	level text and format control elements.
	"""
	def paragraph(self, text):
		return ['\n', text, '\n']
	
	def table(self, header, body):
		return []
	
	def table_row(self, content):
		return []
	
	# flags['header'] true/false if header cell
	# flags['align'] cell alignment
	def table_cell(self, content, **flags):
		return []
	
	# Span level
	
	def autolink(self, link, is_email=False):
		return [
			# underline
			27, 45, 1,
			link,
			27, 45, 0
		]
	
	def codespan(self, text):
		return [text]
		
	def double_emphasis(self, text):
		return [
			# bold
			29, 69, 1,
			text[0],
			29, 69, 0
		]
		
	def emphasis(self, text):
		return [
			# underline
			27, 45, 2,
			text[0],
			27, 45, 0
		]
		
	def image(self, src, title, alt_text):
		return []
		#['[%s]' % alt_text]
		
	def linebreak(self):
		return ['\n\n']
		
	def newline(self):
		return ['\n']
	
	def link(self, link, title, content):
		return [
			27, 45, 1,
			content,
			27, 45, 0
		]
		
	def strikethrough(self, text):
		return ['-%s-' % text]
		
	def text(self, text):
		#return [mistune.escape(text)]
		return [text]
		
	def inline_html(self, text):
		return [text]
	
	# Footnotes
	
	# render in tiny font
	
	# For receipt printing, I'd like to display all inline links
	# as footnotes. (Autolinked urls may simply be underlined in
	# place.) Not sure if there is an option to do this; mistune
	# may need to be patched or subclassed to force it to happen.
	
	def footnote_ref(self, key, index):
		return []
	
	def footnote_item(self, key, text):
		return []
	
	def footnotes(self, text):
		return []

c = sys.stdin.read()
atpr = ATPRenderer()
md = mistune.Markdown(renderer=atpr, hard_wrap=False)
contentList = md(c)
print contentList

"""
	Flatten nested list
	http://stackoverflow.com/a/952952
	
		for sublist in contentList:
			for item in sublist:
				yield item
	
	(Probably possible to build the list flat in the first place...)
"""
flatContentList = [item for sublist in contentList for item in sublist]
print flatContentList

"""

	Apply textwrapping to text extracted from the flattened content list.
	(At this point, input markup characters will have been filtered out.)
	
	Count characters between \n to get line width. Insert \ns where necessary.
	
	(Also, could unidecode text spans now. Should do it prior to wrapping in
	case the transliterated version have more or fewer characters.)
	
	Adjacent string elements can be concatenated for simplicity.
	
	Wrap counting continues (jumps) across text spans, resetting only at \n.
	
	So basically:
	
		start at beginning of list
		count = 0
		foreach character:
			if \n
				reset count
			else
				increment count
			
			if count >= limit # 32 or 42
				insert \n at span count; reset counts
				(keep a separate "span count" that *does* reset at each new element...)
				

"""

linemax = 32
linecount = 0

for e in flatContentList:
	
	# skip numeric elements
	if not isinstance(e, str):
		continue
	
	spancount = 0
	
	
	
"""
# contentList is composed of numbers (format control codes),
# strings (text to be printed), and sub-lists that may contain
# the same content. writeMarkdownTree traverses this list
# and sends the control codes and content to the printer.
from atp import *
class md_atp(atp):
	def writeMarkdownTree(self, mdt):
		for e in mdt:
			if isinstance(e, list):
				self.writeMarkdownTree(e)
			if isinstance(e, int):
				self.writeBytes(e)
			if isinstance(e, str):
				self.timeoutWait()
				self.write(e)

p = md_atp()
p.writeMarkdownTree(contentList)
p.feedClear()
"""

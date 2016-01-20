tptxt
=====

Usage
-----

	usage: tptxt.py [-h] [--verbatim] [--dump PATH] [--print] [--copies N]
					[--limit MAX] [--size {small,medium}] [--header]
					[--title TITLE] [--subtitle SUBTITLE]
					[INPUT]

	Prepare a text file for receipt printer.

	positional arguments:
	  INPUT                 Input text file.

	optional arguments:
	  -h, --help            show this help message and exit
	  --verbatim            Assume input text is pre-formatted.
	  --dump PATH           Write formatted text to PATH (- for stdout).
	  --print               Send output to printer.
	  --copies N            Print N copies.
	  --limit MAX           Send output to printer only if total estimated length
							< MAX.
	  --size {small,medium}
							Body font size.
	  --header              Text begins with title and subtitle header lines.
	  --title TITLE         Text title. Overrides title from header if present.
	  --subtitle SUBTITLE   Text subtitle. Overrides subtitle from header if
							present.

Examples
--------

	./tptxt.py txt/masque-original.txt --size small --dump txt/masque-small.txt --header --print
	> Estimated document length: 943 mm (37.1 inches or 3.09 feet)

This command wraps the [input text](txt/masque-original.txt) to 42 characters per line using the default `small` font. The [output](txt/masque-small.txt) looks like this:

![masque-small.txt](txt/masque-small.jpg)
 
 For comparison, here the same text is printed using the `medium` font:

	./tptxt.py txt/masque-original.txt --size medium --dump txt/masque-medium.txt --header --print
	> Estimated document length: 1902 mm (74.9 inches or 6.24 feet)

In this case, the [output](masque-medium.txt) is wrapped to 32 characters per line. It looks like this:

![masque-medium.txt](txt/masque-medium.jpg)

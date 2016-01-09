#!/usr/bin/python

from atp import *

printer = atp(timeout=5)

# Test inverse on & off
printer.inverseOn()
printer.println("Inverse ON")
printer.inverseOff()

# Set justification (right, center, left) -- accepts 'L', 'C', 'R'
printer.justify(printer.RIGHT)
printer.println("Right justified")
printer.justify(printer.CENTER)
printer.println("Center justified")
printer.justify(printer.LEFT)
printer.println("Left justified")

# Test more styles
printer.boldOn()
printer.println("Bold text")
printer.boldOff()

printer.underlineOn()
printer.println("Underlined text")
printer.underlineOff()

printer.setSize(printer.TINY)
printer.println("Tiny")
printer.setSize(printer.TALL)
printer.println("Tall")
printer.setSize(printer.WIDE)
printer.println("Wide")
printer.setSize(printer.LARGE)
printer.println("Large")
printer.setSize(printer.NORMAL)
printer.println("Normal")

printer.justify(printer.CENTER)
printer.println("normal\nline\nspacing")

printer.setLineSpacing(18)
printer.println("Taller\nline\nspacing")
 # Reset to default
printer.setLineSpacing()
printer.justify()

# Barcode examples
printer.feed(1)
# CODE39 is the most common alphanumeric barcode
printer.printBarcode("ADAFRUT", printer.CODE39)
printer.setBarcodeHeight(100)
# Print UPC line on product barcodes
printer.printBarcode("123456789123", printer.UPC_A)

# Print the 75x75 pixel logo in adalogo.py
import gfx.adalogo as adalogo
printer.printBitmap(adalogo.width, adalogo.height, adalogo.data)

# Print the 135x135 pixel QR code in adaqrcode.py
import gfx.adaqrcode as adaqrcode
printer.printBitmap(adaqrcode.width, adaqrcode.height, adaqrcode.data)
printer.println("Adafruit!")
printer.feed(1)

printer.sleep()      # Tell printer to sleep
printer.wake()       # Call wake() before printing again, even if reset
printer.setDefault() # Restore printer to defaults

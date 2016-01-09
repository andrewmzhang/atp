#!/usr/bin/python

# Weather forecast for Raspberry Pi w/Adafruit Mini Thermal Printer.
# Retrieves data from Yahoo! weather, prints current conditions and
# forecasts for next two days.  See timetemp.py for a different
# weather example using nice bitmaps.
# Written by Adafruit Industries.  MIT license.
# 
# Required software includes Adafruit_Thermal and PySerial libraries.
# Other libraries used are part of stock Python install.
# 
# Resources:
# http://www.adafruit.com/products/597 Mini Thermal Receipt Printer
# http://www.adafruit.com/products/600 Printer starter pack

from __future__ import print_function
import urllib, time, sys
from Adafruit_Thermal import *
from xml.dom.minidom import parseString

# WOEID indicates the geographic location for the forecast.  It is
# not a ZIP code or other common indicator.  Instead, it can be found
# by 'manually' visiting http://weather.yahoo.com, entering a location
# and requesting a forecast, then copy the number from the end of the
# current URL string and paste it here.
if len(sys.argv) == 1:
	WOEID = '2364363'
else:
	WOEID = sys.argv[1]

# Dumps one forecast line to the printer
def forecast(idx):
	tag     = 'yweather:forecast'
	day     = dom.getElementsByTagName(tag)[idx].getAttribute('day')
	lo      = dom.getElementsByTagName(tag)[idx].getAttribute('low')
	hi      = dom.getElementsByTagName(tag)[idx].getAttribute('high')
	cond    = dom.getElementsByTagName(tag)[idx].getAttribute('text')
	printer.print(day + ': low ' + lo)
	printer.print(deg)
	printer.print(' high ' + hi)
	printer.println(deg)

printer = Adafruit_Thermal(timeout=5)
deg     = chr(0xf8) # Degree symbol on thermal printer

# Fetch forecast data from Yahoo!, parse resulting XML
dom = parseString(urllib.urlopen(
        'http://weather.yahooapis.com/forecastrss?w=' + WOEID).read())

printer.justify(printer.CENTER)

# Print heading
city = dom.getElementsByTagName('yweather:location')[0].getAttribute('city')
state = dom.getElementsByTagName('yweather:location')[0].getAttribute('region')
#printer.inverseOn()
printer.underlineOn()
printer.println(city + ', ' + state)
#printer.inverseOff()
printer.underlineOff()

# Print current conditions
printer.boldOn()
printer.println('Current:')
printer.boldOff()

printer.println(dom.getElementsByTagName('pubDate')[0].firstChild.data)

printer.justify(printer.LEFT)

temp = dom.getElementsByTagName('yweather:condition')[0].getAttribute('temp')
cond = dom.getElementsByTagName('yweather:condition')[0].getAttribute('text')
printer.print(temp)
printer.print(deg)
printer.println(' ' + cond)

# Print forecast

printer.justify(printer.CENTER)
printer.boldOn()
printer.println('Forecast:')
printer.boldOff()

printer.justify(printer.LEFT)

forecast(0)
forecast(1)
forecast(2)

printer.feed(2)

import urllib
import re

for propertyid in range(1799, 1800):

		x = str(propertyid)

		print "----searching for", x

		htmlfile = urllib.urlopen("http://taweb.pendoreille.org/PropertyAccess/Property.aspx?cid=0&year=2016&prop_id="+x+"")

		htmltext = htmlfile.read()

		regex = '<td class="currency total">(.+?)</td>'

		pattern = re.compile(regex)

		taxes = re.findall (pattern,htmltext)

		if taxes[2:]:

			regex = '<tr><td>Name:</td><td>(.+?)</td><td>Owner ID:</td><td>(.+?)</td></tr>'

			pattern = re.compile(regex)

			ownername = re.findall (pattern,htmltext)

			print ownername
			print taxes
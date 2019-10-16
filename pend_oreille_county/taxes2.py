import requests
from BeautifulSoup import BeautifulSoup


def main():
	for propertyid in range(1799, 1800):

		x = str(propertyid)

		print "----searching for", x

		r = requests.get("http://taweb.pendoreille.org/PropertyAccess/Property.aspx?cid=0&year=2016", params=dict(prop_id=x))
		soup = BeautifulSoup(r.text)

		for taxtable in soup.findAll("tr", "dataRow"):
			taxes = taxtable.find("td", "currency total").text
			if taxes[2:]:
				print taxes
				legal_td = ownerdata.find("td", "propertyDetailsLegalDescription")
				if legal:
					legal = legal_td.text  # here's where we grab the .text property
				else:
					continue  # searching for that item returned nothing, decide if you want to print an error, continue, etc

if __name__ == '__main__':
	main()
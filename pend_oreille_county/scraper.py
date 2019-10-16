#!/usr/bin/env python

import requests
from bs4 import BeautifulSoup
import csv
import os.path
import time

# main url for scraping
URL = r'http://taweb.pendoreille.org/PropertyAccess/Property.aspx?cid=0&year=2016&prop_id={}'
# range of properties ID
PROP_ID_RANGE = (1605, 20000)
# name of the result CSV file
CSV_FILENAME = 'properties.csv'
# maximum number of the consecutive ID of properties that don't exist
MAX_NOT_FOUND_COUNT = 100
# timeout for page downloading
DOWNLOAD_TIMEOUT = 30
# download retry count
DOWNLOAD_RETRY_COUNT = 5

# HTTP-headers
HTTP_HEADERS = {
    'Connection': 'keep-alive',
    'User-Agent': ('Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '+\
                   'Chrome/52.0.2743.116 Safari/537.36'),
    'Accept': ('text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'),
    'Referer': "http://taweb.pendoreille.org/PropertyAccess/SearchResults.aspx?cid=0",
    'Accept-Language': 'q=0.8,en-US;q=0.6,en;q=0.4'
}

def get_value(soup, name, is_market_value=False):
    """Get table value"""
    try:
        value = soup.find("td", text=name).next_sibling
        if is_market_value:
            value = value.next_sibling.text.strip().lstrip('$').replace(',','')
        else:
            value = value.text.strip()
    except:
        value = ''

    return value

def download_page(url):
    # download webpage
    print("\tDownloading a webpage...")
    download_err_count = 0
    while True:
        try:
            r = requests.get(url, headers=HTTP_HEADERS, timeout=DOWNLOAD_TIMEOUT)
        except Exception as e:
            print("Download error: {0!s}".format(e))
            download_err_count += 1
            if download_err_count >= DOWNLOAD_RETRY_COUNT:
                raise
            else:
                time.sleep(3)
        else:
            return r


# path to CSV-file
csv_file_path = os.path.join(os.path.dirname(__file__), CSV_FILENAME)

with open(csv_file_path, 'w', newline='') as csvfile:
    # fields in csv
    fieldnames = [
        "Legal Description",
        "Property ID",
        "Geographic ID",
        "Location Address",
        "Owner Name",
        "Mailing Address",
        "Market Value"
    ]

    # set up csv writer
    csv_writer = csv.DictWriter(csvfile, delimiter=';', quotechar='"',
                                quoting=csv.QUOTE_NONNUMERIC, fieldnames=fieldnames)
    csv_writer.writeheader()

    curr_property = {}
    not_found_count = 0
    # start processing properties
    for property_id in range(*PROP_ID_RANGE):
        print("Processing property #{}...".format(property_id))
        
        # format URL for current property ID
        url = URL.format(property_id)

        # download webpage
        try:
            r = download_page(url)
        except Exception as e:
            print("Maximum download errors exceeded. Probably the website blocks you by IP.")
            break

        # check if download OK
        if not r.ok:
            if r.status_code == requests.codes.NOT_FOUND:
                print('\tThe page for property with ID #{} not found!'.format(
                    property_id
                    )
                )
                continue
            elif r.status_code != requests.codes.OK:
                print('\tThe website returned status code {} ("{}")!'.format(
                    r.status_code,
                    r.reason
                )
                      )
                continue

        # parse webpage
        print('\tParsing the webpage...')
        soup = BeautifulSoup(r.text, 'lxml')

        # find block with data
        details_table = soup.find("table", summary="Property Details")

        # check for "Property not found." message if block not found
        if not details_table:
            if soup.find("p", text="Property not found."):
                print("\tProperty not found, skipped")
                not_found_count += 1
                
                # exit if not found 10 times in a row
                if not_found_count >= MAX_NOT_FOUND_COUNT:
                    print('Not found {0!s} properties in a row, exiting...'.format(not_found_count))
                    break
                continue
            else:
                print('\tWARNING! Table "Property Details" not found!')
                continue

        # reset counter
        not_found_count = 0

        # find table "Pay Tax Due"
        pay_tax_due_table = soup.find(
            "table", 
            id="paymentTaxDuePanel_PaymentTaxDue_paymentTable"
        )
        if not pay_tax_due_table:
            print('\tTable "Pay Tax Due" not found!')
            continue

        # find table rows and check count
        pay_tax_due_rows = pay_tax_due_table.find_all("tr", class_="dataRow")
        if len(pay_tax_due_rows) < 2:
            print('\tTable "Pay Tax Due" has not multiple rows!')
            continue

        # get values
        curr_property["Legal Description"] = get_value(details_table, "Legal Description:")
        curr_property["Property ID"] = property_id
        curr_property["Geographic ID"] = get_value(details_table, "Geographic ID:")
        curr_property["Location Address"] = get_value(details_table, "Address:")
        curr_property["Owner Name"] = get_value(details_table, "Name:")
        curr_property["Mailing Address"] = get_value(details_table, "Mailing Address:")
        curr_property["Market Value"] = int(get_value(soup.find("div", id="valuesDetails"), 
                                                  "(=) Market Value:", True))

        print("\tWriting CSV...")
        csv_writer.writerow(curr_property)
        print("\tDone")
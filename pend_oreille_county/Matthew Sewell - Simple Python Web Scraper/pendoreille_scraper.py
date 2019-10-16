# -*- encoding: utf-8 -*-

import csv
import logging

import requests
from bs4 import BeautifulSoup

start_id = 1600
stop_id = 18000
output_filename = "pendoreille.csv"


class PendoreilleItem:
    def __init__(self, property_id):
        self.property_id = property_id
        self.url = "http://taweb.pendoreille.org/PropertyAccess/Property.aspx?cid=0&year=2016&prop_id={0}".format(
            self.property_id
        )
        self._data = None
        self._soup = None
        self._exists = False
        self.process = False

        self.legal_description = None
        self.geographic_id = None
        self.location_address = None
        self.owner_name = None
        self.mailing_address = None
        self.market_value = None
        self.total_taxes_due = 0

        self._logger = logging.getLogger('item {0}'.format(self.property_id))
        self._logger.setLevel(logging.DEBUG)
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        self._logger.addHandler(ch)

        try:
            self._data = requests.get(
                url=self.url,
            ).text
            self._logger.info("Got data for item")
            self._soup = BeautifulSoup(self._data, "html.parser")
            self._check_validity()
            if self._exists:
                try:
                    if self._is_past_due():
                        self._parse_data()
                        self.process = True
                    else:
                        self._logger.info("Item is not past due, discarding...")
                except:
                    self._logger.info("No tax due data for this item, discarding...")
        except:
            self._logger.warning("Failed to get data")

    def _check_validity(self):
        if not "Property not found." in self._data:
            self._exists = True
            self._logger.info("Item is valid")
        else:
            self._logger.warning("Item is invalid, discarding...")

    def _is_past_due(self):
        due_taxes_table = self._soup.find("table", attrs={"id": "paymentTaxDuePanel_PaymentTaxDue_paymentTable"})
        due_taxes_rows = due_taxes_table.findAll("tr", attrs={"class": "dataRow"})
        if len(due_taxes_rows) >= 3:
            return True
        else:
            return False

    def _parse_data(self):
        try:
            self.legal_description = self._soup.findAll("td", text="Legal Description:")[0].find_next_siblings("td")[
                0].text
        except IndexError:
            self._logger.warning("Failed to find legal description")

        try:
            self.geographic_id = self._soup.findAll("td", text="Geographic ID:")[0].find_next_siblings("td")[0].text
        except IndexError:
            self._logger.warning("Failed to find geographic ID")

        try:
            self.location_address = self._soup.findAll("td", text="Address:")[0].find_next_siblings("td")[0].text
        except IndexError:
            self._logger.warning("Failed to find location address")

        try:
            self.owner_name = self._soup.findAll("td", text="Name:")[0].find_next_siblings("td")[0].text
        except IndexError:
            self._logger.warning("Failed to find owner name")

        try:
            self.mailing_address = self._soup.findAll("td", text="Mailing Address:")[0].find_next_siblings("td")[0].text
        except IndexError:
            self._logger.warning("Failed to find mailing address")

        try:
            self.market_value = self._soup.findAll("td", text="(=) Market Value:")[0].find_next_siblings("td")[1].text
        except IndexError:
            self._logger.warning("Failed to find market value")

        try:
            due_taxes_table = self._soup.find("table", attrs={"id": "paymentTaxDuePanel_PaymentTaxDue_paymentTable"})
            due_taxes_rows = due_taxes_table.findAll("tr", attrs={"class": "dataRow"})

            for row in due_taxes_rows:
                row_due_str = row.find("td", attrs={"class": "currency total"}).text
                row_due_str = row_due_str.replace("$", "")
                row_due = float(row_due_str)
                self.total_taxes_due += row_due
        except:
            self._logger.warning("Failed to find tax due data")

        self._logger.info("Parsed data")


if __name__ == '__main__':
    # define ID to start and stop
    total = 0

    # create csv exporter
    csv_file = open(output_filename, "wb")
    exporter = csv.writer(csv_file, dialect='excel')
    # write header
    exporter.writerow(
        [
            "Property ID",
            "Geographic ID",
            "Legal description",
            "Location address",
            "Owner name",
            "Mailing address",
            "Market value",
            "Total taxes due"
        ]
    )
    csv_file.close()

    # create logger
    logger = logging.getLogger('scraper')
    logger.setLevel(logging.DEBUG)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)

    logger.info("Scraping started. Processing IDs from {0} to {1}".format(start_id, stop_id))

    # start processing
    for item_id in range(start_id, stop_id):
        logger.info("Processing item with ID {0}".format(item_id))
        item = PendoreilleItem(item_id)
        if item.process:
            csv_file = open(output_filename, "ab")
            item_exporter = csv.writer(csv_file, dialect="excel")
            item_exporter.writerow(
                [
                    item.property_id,
                    item.geographic_id,
                    item.legal_description,
                    item.location_address,
                    item.owner_name,
                    item.mailing_address,
                    item.market_value,
                    "${0}".format(item.total_taxes_due)
                ]
            )
            logger.info("Item {0} successfully exported".format(item_id))
            total += 1
            csv_file.close()

    logger.info("Scraping finished. Got {0} valid items".format(total))

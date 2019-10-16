from selenium import webdriver
import csv


browser = webdriver.Chrome()

with open('may.csv', newline='') as csvfile:
	reader = csv.DictReader(csvfile)
	for row in reader:
		try:
			browser.get('https://www.assessor.shelby.tn.us/content.aspx')

			elem = browser.find_element_by_css_selector('#ctl02_txtStreetNumber')
			elem.clear()
			elem.send_keys(row['Street Num'])

			elem = browser.find_element_by_css_selector('#ctl02_txtStreetName')
			elem.clear()
			elem.send_keys(row['Street'])

			browser.find_element_by_css_selector('#ctl02_btnStreetSearch').click()
			browser.find_element_by_css_selector('#dgList_HyperLink1_0').click()
			value = browser.find_element_by_css_selector('#spnTotalAppraisal').text.strip('$ ')
			brick = browser.find_element_by_css_selector('#spnExteriorWalls').text
			year = browser.find_element_by_css_selector('#spnYearBuilt').text
			if 'BRICK' in brick:
				print(True)
			else:
				print(False)
			# print(value)
		except:
			print(0.00)

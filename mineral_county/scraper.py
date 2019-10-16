import requests
from bs4 import BeautifulSoup
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
import re
from multiprocessing import Pool
import os


Base = declarative_base()

class Property(Base):
	__tablename__ = 'properties'
	id = Column(Integer, primary_key=True)
	tax_id = Column(String)
	leased = Column(Boolean)
	delinquent = Column(Integer)
	acres = Column(Integer)
	error = Column(Boolean)

	def __repr__(self):
		return "<Property(tax_id='%s')>" % (self.tax_id)

engine = create_engine(os.getenv('DB'), echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) \
    AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36'}

def property(instance):
	print('************' + instance.tax_id + '************************')
	r = requests.get(f'http://www.mtcounty.com/bmsrdl/bmsrdl.php?customer_id=105&ntax_id={instance.tax_id}&xdate=MTIvMDYvMjAxOA==&propyear=2018&Histyear=10&gcity=LOLO&header_text=Detail&body_include=tax_search_selection&current_app=tax&func=webtax2', headers=headers)
	soup = BeautifulSoup(r.text, 'html.parser')
	try:
		soup2 = soup.find('font').text
		value = 17 if 'Total for 17' in soup2 else 18 if 'Total for 18' in soup2 else 0
		if value != 0:
			print('Delinquent since {}'.format(2000 + value))
			instance.delinquent = 2000 + value
			if 'LEASE' in soup2:
				print('leased')
				instance.leased = True
			else:
				instance.leased = False
			land = re.findall('ACRES [0-9]{1,3}\.[0-9]{1,2}', soup2)
			instance.acres = 0 if not isinstance(land, int) else land
		else:
			instance.delinquent = value
			print('No taxes due')
		instance.error = False
		session.add(instance)
	except AttributeError:
		if soup.find('pre').text is None:
			print('The soup is not warm')
			instance.error = True
		if 'Tax ID {} not found!'.format(instance.tax_id) in soup.find('pre').text:
			session.delete(instance)
			print(instance.tax_id + ' was deleted')
		elif 'No Taxes Currently Owed to the County!' in soup.find('pre').text:
			print('No Taxes are owed')
		else:
			print('Something else is going on with ' + instance.tax_id)
			instance.error = True
			session.add(instance)

	session.commit()

p = Pool(2)  # Pool tells how many at a time
records = p.map(property, session.query(Property))
p.terminate()
p.join()
session.close()




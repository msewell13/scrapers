import PyPDF2
import nltk
from nltk.corpus import stopwords
import re
import os
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import 

nltk.download('punkt')

Base = declarative_base()

class Property(Base):
	__tablename__ = 'properties'
	id = Column(Integer, primary_key=True)
	tax_id = Column(String(16))
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

pdfFileObj = open('report.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

pages = pdfReader.numPages
text = ""

for page in range(pages):
	pageObj = pdfReader.getPage(page)
	text += pageObj.extractText()
	print(page)

matches = re.findall('[0-9]{3,7}', text)
tokens = nltk.word_tokenize(text)
punctuations = ['(',')',';',':','[',']',',',"--"]
# stop_words = stopwords.words(re.search('[^\d\W]', tokens))
# keywords = [word for word in tokens if not word in matches and not word in punctuations]
keywords = [word for word in tokens if not word in punctuations and word in matches]
new_list = list(set(keywords))

for word in new_list:
	item = Property(tax_id=word)
	session.add(item)

session.commit()
session.close()




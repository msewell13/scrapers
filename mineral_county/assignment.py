import markdown
from flask import Flask, render_template, Markup
import datetime
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Property(Base):
	__tablename__ = 'properties'
	id = Column(Integer, primary_key=True)
	tax_id = Column(String)
	owner = Column(String)
	address = Column(String)
	legal = Column(String)
	parcel = Column(String)
	geo = Column(String)


	def __repr__(self):
		return "<Property(tax_id='%s')>" % (self.tax_id)

engine = create_engine('sqlite:///mineral2.db', echo=True)
Base.metadata.create_all(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()


app = Flask(__name__)
@app.route('/')
def index():
	tax_id = '468800'
	owner = 'CRAIN RANCH LLP'
	address = 'PO BOX 402, SAINT REGIS, MT 59866-0402'
	legal = 'TRICON MAJOR, S30, T18 N, R27 W, Lot 6, ACRES 9.534'
	parcel = '54-2744-30-2-04-06-0000'
	geo = '54-2744-30-2-04-06-0000'

	prop = Property(
		tax_id=tax_id,
		owner=owner,
		address=address,
		legal=legal,
		parcel=parcel,
		geo=geo)
	session.add(prop)
	session.commit()
	session.close()

	content = f"""
<center>
NOTICE OF PENDING ASSIGNMENT<br>
(Pursuant to 15-17-212(3) and 15-17-323(5), MCA)<br>
**<u>NOTICE EXPIRES 60 DAYS FROM DATE OF NOTICE</u>**
</center>


**<u>THIS NOTICE IS VERY IMPORTANT</u>** with regard to the purchase of the Tax Sale Certificate, which Mineral County holds on the following property. If the delinquent taxes are not paid in **<u>IN FULL</u>** within **<u>2 WEEKS</u>** from the date of this notice, an assignment of Tax Sale Certificate will be purchased, **THIS COULD RESULT IN THE LOSS OF YOUR PROPERTY LISTED BELOW.**

Please direct any questions to:<br>
Mineral County Treasurer<br>
PO Box 100<br>
Superior, MT 59872

406-822-3530

**OWNER OF RECORD:**<br>
{owner}

**MAILING ADDRESS OF OWNER OF RECORD:**<br>
{address}

**LEGAL DESCRIPTION:**<br>
{legal}

**PARCEL NUMBER:**<br>
{parcel}

**GEO CODE:**<br>
{geo}

**DATE OF NOTICE:**<br>
{datetime.datetime.today().strftime('%Y-%m-%d')}


<br>
<br>
<br>
<br>



Matthew Sewell<br>
Member, J&M Montana Rentals, LLC
"""
	content = Markup(markdown.markdown(content))
	return render_template('index.html', **locals())

app.run(debug=True)
# Mineral County Tax Lien Scraper

This application will pull down all of the delinquent tax parcels within Mineral County Montana.

app.py parses a pdf of every single parcel within the county and uses that to extract a tax id number and saves it to a sqlite database.

scraper.py will read the tax id numbers in the sqlite database retrieved from app.py and use it to check if they are delinquent or not. Please note that the tax years will need to be updated as time passes on. Also, if the county updates their website it will break this software and will need to be re-written.

Once you have identified which tax liens you would like to buy, you need to send the property owner a certified letter. Assignment.py will help you craft these letters
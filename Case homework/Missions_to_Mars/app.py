# -*- coding: utf-8 -*-
"""
Created on Sun Jan  3 20:59:21 2021

@author: brook
"""

#%%

from flask import Flask, render_template
import pandas as pd
import pymongo
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import scrape_mars


#%%

# Instantiate flask app
app = Flask(__name__)


#%%

# Configure ChromeDriver
# executable path = {'executable_path': ChromeDriverManager().install()}
# browser = Browser('chrome', **executable_path)


#%%

# Connect to MongoDB
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)

# Connect to mars_app MongoDB database
db = client.mars_app

# Connect to mars collection of mars_app MongoDB database
mars = db.mars


#%%

@app.route('/')
def index():
    # some code here
    
@app.route('/scrape')
def scrape():
    
    # Connect to mars_app MongoDB database
    db = client.mars_app
    
    # Connect to mars collection
    mars = db.mars
    
    # Gather 2 documents (dictionaries) to insert into mars collection
    # named (1) mars_dict and (2) mars_hemispheres_dict
    # scrape_all() was created in teh scrape_mars.py file
    # It is accessed by import (see above)
    scrape_all()
    
    # Upsert #1 into the mars collection (preferred to avoid duplicates)
    mars.update_one({}, {'$set': mars_dict}, upsert=True)
    
    # Upsert #2 into the mars collection (preferred to avoid duplicates)
    mars.update_one({}, {'$set': mars_hemispheres_dict}, upsert=True)

if __name__ == '__main__':
    app.run(debut=True)




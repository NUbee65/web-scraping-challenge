#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Dependencies
import requests
from splinter import Browser
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import pymongo


# In[2]:


# Configure ChromeDriver / Setup Splinter
executable_path = {'executable_path': ChromeDriverManager().install()}
browser = Browser('chrome', **executable_path, headless=False)


# ## Step 1 - Scraping

# ### A. NASA Mars News

# In[3]:


def mars_news():
    
    url = 'https://mars.nasa.gov/news'
    browser.visit(url)
    
    html = browser.html
    news_soup = BeautifulSoup(html, 'html.parser')
    
    article_container = news_soup.find('ul', class_='item_list')
    
    article_date = article_container.find('div', class_='list_date').text
    article_title = article_container.find('div', class_='content_title').text
    article_summary = article_container.find('div', class_='article_teaser_body').text.strip()
    
    return article_date, article_title, article_summary


# ### B1. JPL Space Images - Featured Image

# #### Convert above code into a function named "featured_image()" using Method 1 (which returned the larger image)

# In[4]:


def featured_image():
    
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    
    html = browser.html
    featured_image_soup_1 = BeautifulSoup(html, 'html.parser')
    
    featured_image_title = featured_image_soup_1.find('h1', 'media_feature_title').text.strip()
    
    featured_image_element_m1 = featured_image_soup_1.find('article', class_='carousel_item')['style']
    image_url_m1 = featured_image_element_m1.replace("background-image: url('", '')
    image_url_m1 = image_url_m1.replace("');", '')
    image_url_m1 = f'https://www.jpl.nasa.gov{image_url_m1}'
    featured_image_url = image_url_m1
    
    return featured_image_title, featured_image_url


# ### B1. Mars Facts

# #### Convert above code into a function named "mars_facts()"

# In[5]:


def mars_facts():
    
    url = 'https://space-facts.com/mars/'
    browser.visit(url)
    
    mars_facts_df = pd.read_html(url)
    mars_facts_df = mars_facts_df[0]
    mars_facts_df.columns = ['Planet Metric', 'Mars']
    
    mars_facts_html = mars_facts_df.to_html(classes='table table=striped', index=False, justify='left', border=0)
    
    return mars_facts_html


# ### C. Mars Hemispheres

# #### Convert above code into a function named "mars_hemispheres()"

# In[6]:


def mars_hemispheres():

    # Initiate empty list of dictionaries (no dictionaries yet present)
    global hemisphere_image_urls
    hemisphere_image_urls = []
    
    # URL of page to be scraped and Configure Splinter
    # URL = universal resource locator (FYI)
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    # Capture HTML from URL
    html = browser.html

    # Get list of hemispheres 
    links = browser.find_by_css("a.product-item h3")

    # Traverse Splinter links
    for i in range(len(links)):

        #Find the elements on each loop 
        browser.find_by_css("a.product-item h3")[i].click()

        # Capture HTML from second URL (linked page)
        html = browser.html

        # Parse HTML from second URL (linked page) with BeautifulSoup
        mars_hemispheres_image_soup = BeautifulSoup(html, 'html.parser')

        # Use BeautifulSoup to zero in on image_title
        mars_hemispheres_image_title = mars_hemispheres_image_soup.find('h2', class_='title').text

        # Use BeautifulSoup to zero in on relative URL for wide_image (full image)
        mars_hemispheres_image_url = mars_hemispheres_image_soup.find('img', class_='wide-image')['src']

        # Augment relative URL to create full URL for wide_image (full image)
        mars_hemispheres_image_url = 'https://astrogeology.usgs.gov' + mars_hemispheres_image_url

        # Initiate empty dictionary
        hemisphere_dict = {}

        # Populate dictionary with results
        hemisphere_dict = {"title": mars_hemispheres_image_title, "img_url": mars_hemispheres_image_url}

        # Append dictionary to list of dictionaries
        hemisphere_image_urls.append(hemisphere_dict)

        # Use Splinter to go back to prior web page
        browser.back()
        
    return hemisphere_image_urls

mars_hemispheres()


# ### Create single function to pull all data but the hemispheres portion

# #### Convert above code into a function named "scrape_all()"

# In[7]:


def scrape_all():
    article_date, article_title, article_summary  = mars_news()
    featured_image_title, featured_image_url = featured_image()
    mars_facts_html = mars_facts()
    
    global mars_dict
    
    mars_dict = {
        'article_date': article_date, 
        'article_title': article_title,
        'article_summary': article_summary,
        'featured_image_title': featured_image_title, 
        'featured_image_url': featured_image_url,
        'mars_facts_html': mars_facts_html
    }
    
    return mars_dict


# ### Create dataframe out of hemispheres list of dictionaries

# In[8]:


mars_hemispheres_df = pd.DataFrame(hemisphere_image_urls)
mars_hemispheres_df = mars_hemispheres_df.rename(columns={"title": "mars_hemispheres_title", 
                                                          "img_url": "mars_hemispheres_img_url"})
mars_hemispheres_df.set_index("mars_hemispheres_title", inplace=True)
mars_hemispheres_df


# ### Insert into MongoDB

# In[9]:


# Initialize pymongo to work with MongoDBs
conn = 'mongodb://localhost:27017'
client = pymongo.MongoClient(conn)


# In[10]:


# Connect to mars_app database
db = client.mars_app

# Connect to mars collection
mars = db.mars


# In[11]:


# Dictionary to insert
mars_dict = scrape_all()


# In[12]:


# Insert mars_dict dictionary as a document into mars collection of mars_app MongoDB database
# Importantly, we use UPSERT method, which updates existing documents and adds documents if they don't exist
mars.update_one({}, {'$set': mars_dict}, upsert=True)


# In[13]:


# Convert mars_hemispheres_df DataFrame into dictionary called mars_hemispheres_dict, 
# which is then inserted into mars collection of mars_app MongoDB database
# Importantly, we use UPSERT method, which updates existing documents and adds documents if they don't exist
mars_hemispheres_dict = mars_hemispheres_df.to_dict()
mars.update_one({}, {'$set': mars_hemispheres_dict}, upsert=True)


# In[ ]:





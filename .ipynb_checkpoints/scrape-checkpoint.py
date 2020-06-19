# Imports
import pandas as pd
import requests
import os
import time
from bs4 import BeautifulSoup
from splinter import Browser

def scrape_nasa_news():
    '''
    creates a 2 item list of the title and description 
    of the latest nasa news article
    returns [title, summary]
    '''
    # Scrape the NASA Mars News Site and collect the latest News Title and Paragraph Text.
    # https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest
    # makes the request and the soup
    url_nasa_news = 'https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest'
    response = requests.get(url_nasa_news)
    nasa_soup = BeautifulSoup(response.text, 'html.parser')
    
    # finds and extracts the target data
    nasa_news_title_raw = nasa_soup.find('div', class_='content_title').text
    nasa_news_desc_raw = nasa_soup.find('div', class_='slide').find('div', class_='rollover_description').text
    
    # cleans the strings
    nasa_news_title = nasa_news_title_raw.replace('\n', '')
    nasa_news_desc = nasa_news_desc_raw.replace('\n', '')
    
    # returns the list
    return [nasa_news_title, nasa_news_desc]

def scrape_featured_img():
    '''
    returns the url of the featured space img and the title
    [title, url]
    '''
    # scrape and save the featured image
    # https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars
    # make request and soup
    url_featured_img = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    response = requests.get(url_featured_img)
    img_soup = BeautifulSoup(response.text, 'html.parser')
    
    # builds the url to find the img
    url_img_part_a = 'https://www.jpl.nasa.gov'
    url_img_part_b = img_soup.find('div', class_='carousel_items').a['data-fancybox-href']
    featured_img_url = url_img_part_a + url_img_part_b
    
    # saves the img title
    raw_img_title = img_soup.find('div', class_='carousel_items').h1.text
    img_title = raw_img_title.replace('\r','').replace('\n','').replace('\t','').strip()
    
    return [img_title, featured_img_url]

def init_browser():
    # splinter browser activation
    executable_path = {"executable_path": "chromedriver.exe"}
    return Browser("chrome", **executable_path, headless=False)

def scrape_twiter_mars_weather():
    # collect the most recent tweet from the Mars Weather twitter account
    # https://twitter.com/marswxreport?lang=en
    # use splinter
    url_mars_weather = 'https://twitter.com/marswxreport?lang=en'
    # splinter browser bit
    browser = init_browser()
    browser.visit(url_mars_weather)
    time.sleep(2)
    weather_html = browser.html
    weather_soup = BeautifulSoup(weather_html, "html.parser")
    browser.quit()
    
    print('Done with the browser')
    mars_weather = weather_soup.body.div.main.article.find('div', lang='en').text
    
    return mars_weather

def scrape_mars_facts():
    # Collect and convert the html table from
    # https://space-facts.com/mars/
    url_mars_facts = 'https://space-facts.com/mars/'
    response = requests.get(url_mars_facts)
    facts_soup = BeautifulSoup(response.text, 'html.parser')
    
    # pull the table
    facts_table_list = facts_soup.table.find_all('td')
    
    # each td in the list is on both sides
    # description -> data -> description.
    # they alternate back and forth
    fact_text_list = []
    for fact in facts_table_list:
        fact_text_list.append(fact.text)
        
    # split apart the titels and data
    x = 0
    fact_title = []
    fact_data = []
    for text in fact_text_list:
        if (x%2 == 0):
            fact_title.append(text)
            x+=1
        else:
            fact_data.append(text)
            x+=1
    # make a dict of the table using the titels as keys
    # and the data as the value
    dict_fact_table = {}
    for i in range(len(fact_title)):
        dict_fact_table[fact_title[i]] = fact_data[i]
    
    df = pd.DataFrame(dict_fact_table, index=[0])
    df = df.T
    df.columns = ['Value']
    html_table = df.to_html()
    return html_table

def scrape_hemi_imgs():
    # Obtain a hq img url for each of mars's 4 hemmispheres
    # https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars
    url_mars_hemi = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    response = requests.get(url_mars_hemi)
    hemi_soup = BeautifulSoup(response.text, 'html.parser')
    
    hemi_a_tags = hemi_soup.body.find('div', class_ = 'container').find_all('a')
    
    hemi_img_base_urls = []
    hemi_img_titels = []
    for tag in hemi_a_tags:
        hemi_img_base_urls.append(tag['href'])
        hemi_img_titels.append(tag.text)
    hemi_img_base_urls.pop(0)
    hemi_img_titels.pop(0)
    
    hemi_final_urls = []
    base_hemi_url = 'https://astrogeology.usgs.gov'
    for target in hemi_img_base_urls:
        url = base_hemi_url + target
        response = requests.get(url)
        hemi_img_soup = BeautifulSoup(response.text, 'html.parser')
        hemi_final_urls.append(hemi_img_soup.body.find('div', class_ = 'container').find('div', class_ = 'downloads').a['href'])
    
    hemisphere_image_urls = []
    for x in range(len(hemi_img_titels)):
        dit = {}
        dit['title'] = hemi_img_titels[x]
        dit['img_url'] = hemi_final_urls[x]
        hemisphere_image_urls.append(dit)
    
    return hemisphere_image_urls

def scrape():
    featured_img = scrape_featured_img()
    nasa_news = scrape_nasa_news()
    hemi_imgs = scrape_hemi_imgs()
    mars_weather = scrape_twiter_mars_weather()
    facts = scrape_mars_facts()
    data = {'news' : nasa_news,
            'img' : featured_img,
            'weather' : mars_weather,
            'facts' : facts,
            "hemi" : hemi_imgs
           }
    return data

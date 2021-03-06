#Import Splinter and BS
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver

import datetime as dt

#executable_path = {'executable_path': ChromeDriverManager().install()}
#browser = Browser('chrome', **executable_path, headless=False)

def scrape_all():
    executable_path = {'executable_path': ChromeDriverManager()}
    browser = Browser('chrome', **executable_path, headless=True)

    news_title, news_paragraph = mars_news(browser)

#Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "last_modified": dt.datetime.now(),
        "hemispheres": mars_hemi(browser)
    }

    #Stop webdriver and return
    #browser.quit()
    return data 

def mars_news(browser):

    #Scrape Mars News
    #Mars nasa news site
    url = 'https://www.redplanetscience.com/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css('div.list_text', wait_time=1)

    #Convert the browser html to a soup obj and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

#Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        #Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()

        #Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()

    except AttributeError:  
        return None, None 

    return news_title, news_p


### Featured Images

#(Setup)Visit URL

def featured_image(browser):

    #Visit URL
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    #Find and click the full image button
    full_image_elem = browser.find_by_tag('button')[1]
    full_image_elem.click()

    #Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    try:
        #Find the relative image url
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')


        #Use the base URL to create an absolute URL
        img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    except AttributeError:
        return None

    #Use the base url to create an absolute url
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'

    return img_url


# ## Mars Facts

def mars_facts():

    #Table scrape w/Pandas read_html
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]

    except BaseException:
        return None

    #Assign columns and set index of DF
    df.columns=['Description', 'Mars', 'Earth']
    df.set_index('Description', inplace=True)


#Convert DF to HTML format, add bootstrap
    return df.to_html(justify="left", border = 2, classes="table table-striped table-responsive")


#Mars Hemi
def mars_hemi(browser):
    url = 'https://marshemispheres.com/'
    browser.visit(url)
    # 2. Create a list to hold the images and titles
    hemisphere_image_urls = []

    #Loop through 
    for i in range(4):
        browser.find_by_css("a.product-item img")[i].click()
        full_url = browser.find_by_text("Sample")["href"]
        title = browser.find_by_css("h2.title").text
        mars_dic = {} 
        mars_dic["title"] = title 
        mars_dic["img_url"] = full_url
        hemisphere_image_urls.append(mars_dic) 
        browser.back()
    return hemisphere_image_urls


if __name__ == "__main__":

    #If running as script, print scraped data
        print(scrape_all())

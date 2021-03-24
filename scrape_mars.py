import traceback
import sys
from bs4 import BeautifulSoup as bs
import pandas as pd
from splinter import Browser
from webdriver_manager.chrome import ChromeDriverManager

# Websites to scrape
nasa_mars_news_url = "https://mars.nasa.gov/news/"
jpl_mars_space_images_url = "https://data-class-jpl-space.s3.amazonaws.com/JPL_Space/index.html"
mars_facts_url = "https://space-facts.com/mars/"
astrogeology_url = "https://astrogeology.usgs.gov"
mars_hemispheres_url = astrogeology_url + "/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"

class ChromeBrowser(object): 
	"""
	"""
	def __init__(self, url=None):
		self.url = url 
	  
	def __enter__(self): 
		executable_path = {'executable_path': ChromeDriverManager().install()}
		self.browser = Browser('chrome', **executable_path, headless=False)
		if (self.url):
			self.browser.visit(self.url)
		return self.browser
  
	def __exit__(self, exc_type, exc_val, exc_tb):
		if (exc_type is not None):
			traceback.print_exception(exc_type, exc_val, exc_tb)
		if (self.browser is not None):
			self.browser.quit() 
		return True

def get_nasa_mars_news(browser):
	"""
		Scrape the NASA Mars News Site and collect the latest News Title 
		and Paragraph Text. Assign the 
		text to variables that you can 
		reference later.
	"""

	browser.visit(nasa_mars_news_url)

	html = browser.html
	soup = bs(html, "html.parser")
	
	news_title = soup.find('div', class_='content_title').text
	news_p = soup.find('div', class_='article_teaser_body').text
	
	return news_title, news_p

def get_jpl_mars_space_images(browser):
	"""
	Use splinter to navigate the site and find the image url 
	for the current Featured Mars Image and assign the url 
	string to a variable called `featured_image_url`.

	Make sure to find the image url to the full size `.jpg` image.

	Make sure to save a complete url string for this image.
	"""

	browser.visit(jpl_mars_space_images_url)

	html = browser.html
	soup = bs(html, "html.parser")
	browser.links.find_by_partial_text("FULL IMAGE").click()
	html = browser.html
	soup = bs(html, "html.parser")
	featured_image_url = jpl_mars_space_images_url.replace("index.html", soup.find(class_="fancybox-image")["src"]) 
		
	return featured_image_url

def get_mars_facts():
	"""
	Visit the Mars Facts webpage and use Pandas to scrape the table
	containing facts about the planet including Diameter, Mass, etc.

	Use Pandas to convert the data to a HTML table string.
	"""

	mars_facts = pd.read_html(mars_facts_url, match="Mars")[0]
	mars_facts = mars_facts.set_index("Mars - Earth Comparison", drop=True)
	mars_facts = mars_facts.transpose()
	mars_facts.columns = [col.replace(":","") for col in mars_facts.columns]
	mars_facts = mars_facts.drop("Earth")
	mars_facts = mars_facts.transpose()

	return mars_facts

def get_mars_hemispheres(browser):
	"""
	# Visit the USGS Astrogeology site to obtain high resolution images
	# for each of Mar's hemispheres.

	# You will need to click each of the links to the hemispheres in 
	# order to find the image url to the full resolution image.

	# Save both the image url string for the full resolution hemisphere 
	# image, and the Hemisphere title containing the hemisphere name. 
	# Use a Python dictionary to store the data using the keys `img_url`
	# and `title`.

	# Append the dictionary with the image url string and the hemisphere 
	# title to a list. This list will contain one dictionary for each
	# hemisphere.
	"""

	hemisphere_image_urls = []

	browser.visit(mars_hemispheres_url)

	html = browser.html
	soup = bs(html, "html.parser")
	results = soup.find(class_="result-list").find_all(class_="item")

	for result in results:
		hemisphere = {}
		hemisphere["title"] = result.find("h3").text
		browser.links.find_by_partial_text(hemisphere["title"]).click()
		html = browser.html
		soup = bs(html, "html.parser")
		hemisphere["img_url"] = astrogeology_url + soup.find(class_="wide-image")["src"]
		hemisphere_image_urls.append(hemisphere)
		browser.back()

	return hemisphere_image_urls

def scrape():

	data = {}

	with ChromeBrowser() as browser: 
		news_title, news_p = get_nasa_mars_news(browser)
		data["news_title"] = news_title
		data["news_p"] = news_p

		featured_image_url = get_jpl_mars_space_images(browser)
		data["featured_image_url"] = featured_image_url

		mars_facts = get_mars_facts()
		data["mars_facts"] = mars_facts.to_json()
		
		hemisphere_image_urls = get_mars_hemispheres(browser)
		data["hemisphere_image_urls"] = hemisphere_image_urls

	return data

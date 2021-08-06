from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Open chromedriver
driver = webdriver.Chrome("./chromedriver")
driver.get("https://www.google.com/maps/")

# Search for 'KEYWORDS' in google Maps, and waits for 4 seconds to load. 
# KEYWORDS must be detailed : so that Google Maps show only one result.
# (i.e KEYWORD 세븐일레븐 will search for every place, but 세븐일레븐 혜화점 will indicate only one place)
KEYWORDS = "세븐일레븐 혜화점"
searchbox = driver.find_element_by_css_selector("input#searchboxinput")
searchbox.send_keys(KEYWORDS)

searchbutton = driver.find_element_by_css_selector("button#searchbox-searchbutton")
searchbutton.click()

time.sleep(4)

# Click All Reviews button, and waits for 4 seconds to load
reviewbutton = driver.find_element_by_css_selector("button.gm2-button-alt.HHrUdb-v3pZbf")
reviewbutton.click()

time.sleep(4)

# Load all elements indicating each reviews, scroll reviews till the end of review list
try:
    reviewElement = driver.find_elements_by_css_selector("#pane > div.widget-pane > div.widget-pane-content > div.widget-pane-content-holder > div.section-layout > div.section-layout.section-scrollbox > div.section-layout")[3]
except IndexError:
    reviewElement = driver.find_elements_by_css_selector("#pane > div.widget-pane > div.widget-pane-content > div.widget-pane-content-holder > div.section-layout > div.section-layout.section-scrollbox > div.section-layout")[2]

previousLastReview=None
while True:
    time.sleep(1.3)
    reviews = reviewElement.find_elements_by_xpath("//div[contains(@data-review-id, 'Ch')]")
    lastReview = reviews[-1]
    driver.execute_script('arguments[0].scrollIntoView(true);', lastReview)
    if previousLastReview != lastReview:
        previousLastReview = lastReview
    else:
        break

# Print reviewers
for c in reviews:
    reviewer = c.get_attribute("aria-label")
    if reviewer is not None:
        print(reviewer)

driver.close()
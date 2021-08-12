from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from sys import platform
from tqdm import tqdm
import getopt
import sys
import time

def openChromeDriver():
    # Open chromedriver
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--log-level=3')
    if platform == "linux":
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--single-process')
        chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome("./chromedriver", chrome_options=chrome_options)
    return driver

def getReviewer(placename):
    driver = openChromeDriver()
    driver.get("https://www.google.com/maps/")

    # Search for 'KEYWORDS' in google Maps, and waits for 4 seconds to load. 
    # KEYWORDS must be detailed : so that Google Maps show only one result.
    # (i.e KEYWORD 세븐일레븐 will search for every place, but 세븐일레븐 혜화점 will indicate only one place)
    KEYWORDS = placename
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

def getReviewerIter(placeList, verbose):
    isPrintOnConsole = False
    isPrintSeleniumOper = False

    if verbose == '1':
        isPrintOnConsole = True
    elif verbose == '2':
        isPrintOnConsole = True
        isPrintSeleniumOper = True

    driver = openChromeDriver()
    driver.get("https://www.google.com/maps/")

    placeListFile = open("./"+placeList, "r", encoding='UTF-8')
    reviewerListFile = open("./reviewer.txt", "w")
    errorListFile = open("./errors.txt", "w")

    for place in tqdm(placeListFile.read().splitlines()):
        try:
            # Search for 'KEYWORDS' in google Maps, and waits for 4 seconds to load. 
            # KEYWORDS must be detailed : so that Google Maps show only one result.
            # (i.e KEYWORD 세븐일레븐 will search for every place, but 세븐일레븐 혜화점 will indicate only one place)
            if isPrintOnConsole is True:
                tqdm.write("["+place+"]")

            reviewerListFile.write("["+place+"]\n")

            searchbox = driver.find_element_by_css_selector("input#searchboxinput")
            searchbox.clear()
            searchbox.send_keys(place)

            searchbutton = driver.find_element_by_css_selector("button#searchbox-searchbutton")
            searchbutton.click()

            time.sleep(4)

            try:
                # Click All Reviews button, and waits for 4 seconds to load
                reviewbutton = driver.find_element_by_css_selector("button.gm2-button-alt.HHrUdb-v3pZbf")
                reviewbutton.click()
            except NoSuchElementException:
                if isPrintOnConsole is True:
                    tqdm.write("No Reviews.\n")

                reviewerListFile.write("No Reviews.\n\n")
                time.sleep(1)
                continue

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
                    if isPrintOnConsole:
                        tqdm.write(reviewer)
                    reviewerListFile.write(reviewer+'\n')

            if isPrintOnConsole:
                tqdm.write('\n')
            reviewerListFile.write('\n')
            backbutton = driver.find_element_by_xpath("//button[@aria-label='Back']")
            backbutton.click()
            time.sleep(4)
        except Exception as e:
            if isPrintOnConsole:
                tqdm.write(place+" - Error occured : "+str(e))
            
            errorListFile.write("Error occured : "+str(e)+"\n")
            driver.close()
            driver = openChromeDriver()
            driver.get("https://www.google.com/maps/")
            time.sleep(2)

    driver.close()


def crawlhelp():
    print("\nScrape review information from Google Maps.\n")
    print("required arguments:")
    print("  -m [MODE], --mode [MODE]")
    print("      set mode of scraper. 4 strings are available.")
    print("        reviewer : get all reviewers from input string which indicates place")
    print("        reviewer_fromlist : get all reviewers from input file. file must be list of places you want to search for")
    print("        review : get all reviews from input string which indicates place")
    print("        review_fromlist : get all reviews from input file. file must be list of places you want to search for\n")
    print("  -i [FILE or STRING], --input [FILE or STRING]")
    print("      input of scraper. must be string or filename.")
    print("      [reviewer, review] needs input as string, [reviewer_fromlist, review_fromlist] needs input as filename.")

def main(argv):
    INPUT = None
    EXECMODE = None
    VERBOSE = 0

    try:
        opts, args = getopt.getopt(argv[1:], "hm:i:v:", ["help", "mode=", "input=", "verbose="])
    except getopt.GetoptError:
        print("invalid arguments.")
        crawlhelp()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            crawlhelp()
        elif opt == '-m':
            if arg is not None:
                EXECMODE = arg
            else:
                print("["+arg+"] is invalid mode. Must be one of [reviewer, reviewer_fromlist, review, review_fromlist]")
                sys.exit(2)
        elif opt == '-i':
            INPUT = arg
        elif opt == '-v':
            VERBOSE = arg
    
    if EXECMODE is None:
        print("Need -m or --mode.")
        crawlhelp()
        sys.exit(2)
    elif EXECMODE == "reviewer":
        if INPUT is None:
            print("need input as -i or --input.\nInput must be place name you want to search for.")
        else:
            getReviewer(INPUT)
    elif EXECMODE == 'reviewer_fromlist':
        if INPUT is None:
            print("need input as -i or --input.\nInput must be filename which contains list of place name you want to search for.")
        else:
            getReviewerIter(INPUT, VERBOSE)

if __name__ == "__main__":
    main(sys.argv)
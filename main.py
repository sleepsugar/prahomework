### https://github.com/MazarsLabs/hse-rpa

import os
import pandas as pd
from selenium.webdriver.chrome.options import Options
import selenium.webdriver as webdriver
import time
# from wcm import get_credentials
from email.message import EmailMessage
import smtplib
from conf import query, page, receiver, pdf
# query_link = f"https://www.researchgate.net/search/publication?q={query}&page="
query_link = f"https://www.semanticscholar.org/search?q={query}&sort=relevance&pdf={pdf}"

# working paths
working_dir = os.path.dirname(os.path.realpath(__file__))
folder_for_pdf = os.path.join(working_dir, "articles")
webdriver_path = os.path.join(working_dir, "chromedriver")   # proper version https://chromedriver.chromium.org/

# chek if articles directory is exist and create if not
if not os.path.isdir(folder_for_pdf):
    os.mkdir(folder_for_pdf)

# webdriver
chrome_options = Options()
prefs = {
    "download.default_directory": folder_for_pdf,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True
}
chrome_options.add_experimental_option('prefs', prefs)
os.environ["webdriver.chrome.driver"] = webdriver_path

# links_list = [query_link + str(page+1) for page in range(page)]   # create links to follow
links_list = [query_link]

driver = webdriver.Chrome(executable_path=webdriver_path, chrome_options=chrome_options)

final_info = []   # empty dictionary for articles info
for search_link in links_list:
    # get all links to articles from the page
    driver.get(search_link)
    time.sleep(5)
    articles = driver.find_elements_by_class_name("serp-papers__paper-row")

    articles_links = []
    for article in articles:
        try:
            # data-selenium-selector="title-link"
            link = article.find_element_by_css_selector("a[data-selenium-selector='title-link']").get_attribute("href")
            articles_links.append(link)
        except:
            pass

    for link in articles_links:
        # get info of each article
        tmp_info = {}

        driver.get(link)
        time.sleep(5)
        text = driver.find_element_by_class_name("fresh-paper-detail-page__above-the-fold").text
        try:
            textDescription = driver.find_element_by_css_selector("span[data-selenium-selector='text-truncator-text']").text
        except:
            textDescription = "None"

        try:
            linkSources = driver.find_elements_by_css_selector("a[data-selenium-selector='paper-link']")
            if len(linkSources) > 0:
                for link in linkSources:
                    print(link.get_attribute("href"))

                textSource = linkSources[0].get_attribute("href")
                print(textSource)
            else:
                textSource = "None"
        except Exception as e:
            print(e)
            textSource = "None"
        try:
            textNumberOfCitations = driver.find_element_by_class_name("scorecard-stat__headline__dark").text
            print(textNumberOfCitations)
        except:
            textNumberOfCitations = "None"
        try:
            textArticleFile = driver.find_element_by_css_selector("a[data-selenium-selector='paper-link']").get_attribute("href")
        except:
            textArticleFile = "None"

        tmp_info.update({
                                   'title': text.split("\n")[1],
                                   'authors' : text.split("\n")[2],
                                   'source' : textSource.split("\n"),
                                   'number of citations' : textNumberOfCitations.split("\n"),
                                   'article file' : textArticleFile.split("\n"),
                                   'description' : textDescription.split("\n")
                                })

        # trying to download the article's doc
        try:
            initial_dir = os.listdir(folder_for_pdf)
            driver.find_element_by_css_selector("a.icon-button").click()
            time.sleep(5)

            current_dir = os.listdir(folder_for_pdf)

            new_file = list(set(current_dir) - set(initial_dir))
            if len(new_file) > 0:
                filename = new_file[0]
                full_path = os.path.join(folder_for_pdf, filename)
            else:
                # cannot download (because there is not valid links to pdf)
                full_path = None
        except Exception as e:
            print(e)
            full_path = None

        tmp_info.update({'path_to_file': full_path})

        final_info.append(tmp_info.copy())
        time.sleep(2)

driver.quit()

# write all info to excel
df = pd.DataFrame(final_info)
excel_path = os.path.join(working_dir, "data.xlsx")
df.to_excel(excel_path, index=False)
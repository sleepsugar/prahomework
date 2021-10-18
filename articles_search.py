### https://github.com/MazarsLabs/hse-rpa

import os
import pandas as pd
from selenium.webdriver.chrome.options import Options
import selenium.webdriver as webdriver
import time
# from wcm import get_credentials
from email.message import EmailMessage
import smtplib
from conf import query, num_page, receiver

query_link = f"https://www.researchgate.net/search/publication?q={query}&page="

# working paths
working_dir = os.path.dirname(os.path.realpath(__file__))
folder_for_pdf = os.path.join(working_dir, "articles")
webdriver_path = os.path.join(working_dir, "chromedriver")   # proper version https://chromedriver.chromium.org/

# chek if articles directory is exist and create if not
if not os.path.isdir(folder_for_pdf):
    os.mkdir(folder_for_pdf)

# webdriver
chrome_options = Options()
prefs = {"download.default_directory": folder_for_pdf, "download.prompt_for_download": False}
chrome_options.add_experimental_option('prefs', prefs)
os.environ["webdriver.chrome.driver"] = webdriver_path   # 'webdriver' executable needs to be in PATH. Please see https://sites.google.com/a/chromium.org/chromedriver/home

links_list = [query_link + str(page+1) for page in range(num_page)]   # create links to follow

driver = webdriver.Chrome(executable_path=webdriver_path, options=chrome_options)

final_info = []   # empty dictionary for articles info
for search_link in links_list:
    # get all links to articles from the page
    driver.get(search_link)
    time.sleep(5)
    articles = driver.find_elements_by_class_name("nova-legacy-o-stack__item")
    
    articles_links = []
    for article in articles:
        try:
            link = article.find_element_by_css_selector("a.nova-legacy-e-link.nova-legacy-e-link--color-inherit.nova-legacy-e-link--theme-bare").get_attribute("href")
            articles_links.append(link)
        except:
            pass

    for link in articles_links:
        # get info of each article 
        tmp_info = {}

        driver.get(link)
        text = driver.find_element_by_class_name("research-detail-header-section__ie11").text

        tmp_info.update({
                        'title': text.split("\n")[0],
                        'date' : text.split("\n")[1],   # TODO: might convert to datetime
                        'authors': text.split("Authors:")[-1].replace("\n","; ")
                        })

        # trying to download the article's doc
        try:
            initial_dir = os.listdir(folder_for_pdf)
            driver.find_element_by_css_selector("span.nova-legacy-c-button__label.gtm-download-fulltext-btn-header").click()
            time.sleep(5)

            current_dir = os.listdir(folder_for_pdf)
            filename = list(set(current_dir) - set(initial_dir))[0]
            full_path = os.path.join(folder_for_pdf, filename)

        except Exception as e:
            print(e)
            full_path = None

        tmp_info.update({'path_to_file':full_path})

        final_info.append(tmp_info.copy())
        time.sleep(2)

driver.quit()

# write all info to excel
df = pd.DataFrame(final_info)
excel_path = os.path.join(working_dir, "data.xlsx")
df.to_excel(excel_path, index=False)

# create email
# login, password = get_credentials("HSE")   # could be setup manually
# mail = EmailMessage()
# mail['From'] = login
# mail['To'] = receiver
# mail['Subject'] = "Topics analysis"
# mail.set_content("Hi!\n\nFind attached excel file with articles info.\n\nRegard,")
#
# # add attachment
# with open(excel_path, 'rb') as f:
#     file_data = f.read()
#     file_name = f'articles_info.xlsx'
# mail.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
#
# # send email
# server = smtplib.SMTP('smtp.office365.com')
# server.starttls()
# server.login(login, password)
# server.send_message(mail)
# server.quit()
#
#
#     # ┏━┓┏━┓┏━━━┓┏━━━━┓┏━━━┓┏━━━┓┏━━━┓
#     # ┃ ┗┛ ┃┃┏━┓┃┗━━┓ ┃┃┏━┓┃┃┏━┓┃┃┏━┓┃
#     # ┃┏┓┏┓┃┃┃ ┃┃  ┏┛┏┛┃┃ ┃┃┃┗━┛┃┃┗━━┓
#     # ┃┃┃┃┃┃┃┗━┛┃ ┏┛┏┛ ┃┗━┛┃┃┏┓┏┛┗━━┓┃
#     # ┃┃┃┃┃┃┃┏━┓┃┏┛ ┗━┓┃┏━┓┃┃┃┃┗┓┃┗━┛┃
#     # ┗┛┗┛┗┛┗┛ ┗┛┗━━━━┛┗┛ ┗┛┗┛┗━┛┗━━━┛

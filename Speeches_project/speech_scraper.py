from urllib import request
from bs4 import BeautifulSoup as BS
import pandas as pd
import time
from random import randint
import re
from tqdm import tqdm

main_url = "https://www.tccb.gov.tr"
start_url = "https://www.tccb.gov.tr/receptayyiperdogan/konusmalar/"

html = request.urlopen(start_url)
bs = BS(html.read(), "html.parser")

# Get all available pages links
pattern = re.compile(r'=(\d+)')
last_page = bs.find("div", {"class": "paging"}).find_all('a', href=True)[-1]["href"]
last_num = int(pattern.findall(last_page)[0])

site_pages = [main_url + re.sub(str(last_num), str(num), last_page) for num in range(2, last_num+1)]
site_pages.insert(0, start_url)

links_list = []
titles_list = []
dates_list = []
text_list = []

# Iterate over all pages to gather links
for page in tqdm(site_pages, position=0, desc="Gather speech links"):

    # Wait some time before the next request
    time.sleep(1)

    html = request.urlopen(page)
    bs = BS(html.read(), "html.parser")

    # Get link, title and date of each speech
    speech_links = bs.find("div", {"id": "divContentList"}).findAll("a")
    titles_list += [speech.get_text() for speech in speech_links]
    links_list += [main_url+speech["href"] for speech in speech_links]
    speech_dates = bs.find("div", {"id": "divContentList"}).findAll("dt", {"class": "date"})
    dates_list += [speech.get_text() for speech in speech_dates]

# Iterate over each speech link
for link in tqdm(links_list, position=1, desc="Gather speech transcripts"):

    # Wait some time before the next requests
    time.sleep(1)

    html = request.urlopen(link)
    bs = BS(html.read(), "html.parser")
    speech_text = bs.find("div", {"id": "divContentArea"}).find_all(string=True)
    text_list.append("".join(speech_text))

speech_df = pd.DataFrame(list(zip(titles_list, dates_list, text_list)), columns=["Title", "Date", "Text"])
speech_df.Date = pd.to_datetime(speech_df.Date, format="%d.%m.%Y")
speech_df.to_csv("Erdogan_speeches.csv", index=False, date_format="%Y-%m-%d")
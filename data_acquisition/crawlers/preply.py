import requests
import json
import os
import urllib.request
import pandas as pd
from selenium.webdriver.common.action_chains import ActionChains
import datetime
from pathlib import Path
import time
from crawlers.utils import get_url, create_chrome_bot
from random import uniform
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import re


def get_languages(bot):
    bot.get("https://preply.com/en/skype/english-tutors")

    time.sleep(uniform(1, 3))

    languages = []

    # Get all languages in the menu
    list_lang = bot.find_elements_by_css_selector("div.SuggestionItem___3zg9V")
    print("Elements found = {}".format(len(list_lang)))

    for elem in list_lang:
        if ('language' in elem.text):
            languages.append(elem.text)

    return languages


def generate_languages_url(languages):
    languages_url = {}

    for lang in languages:
        lang = lang.replace(' language', '')
        languages_url[lang] = "https://preply.com/en/skype/" + lang.lower() + "-tutors"

    return languages_url


def get_html_from_teachers_list(storing_path, reading_path, language):
    with open(reading_path) as json_file:
        info = json.load(json_file)

    retrieve_teachers_pages(info, storing_path + "teachers_html/" + language)


def visit_language(bot, base_url, language, crawl_size):
    try:
        # Open first page to find recommended teachers
        page_url = base_url + "?page=1"
        get_url(bot, base_url)
        bot.execute_script("window.scrollTo(0, 0);var lenOfPage=document.body.scrollHeight;")
        time.sleep(uniform(3, 5))
        teachers_information = []
        page = 1

        while len(teachers_information) < crawl_size:
            # If page is empty, we return
            teachers = bot.find_elements_by_css_selector("div.TutorCardWrapper___2SCl8")
            if len(teachers) == 0:
                return teachers_information

            soup = BeautifulSoup(bot.page_source, features="html.parser")
            time.sleep(uniform(7, 10))

            divs = soup.findAll('div', {'style': 'display:contents'})
            info_ = [str(text) for text in divs if str(text).startswith('<div style="display:contents"><script type="application/ld+json">')][0]
            teachers_list = json.loads(re.findall('(?<=itemListElement\":)(.*?)\}</script><script', info_)[0])

            for teacher in teachers_list:
                teachers_information.append({'name': teacher['name'], 'url': teacher['url'], 'is_featured': False, 'position': teacher['position'],
            'visited': datetime.datetime.today().strftime('%Y-%m-%d')})

            # Look for featured teachers only in page 1
            if page == 1:
                featured = len(bot.find_elements_by_css_selector("span.FeaturedTutorBadge___I6XCX"))
                if featured:
                    for i in range(featured):
                        teachers_information[i]['is_featured'] = True

            page += 1
            page_url = base_url + "?page={}".format(page)
            get_url(bot, page_url)

        return teachers_information

    except Exception as e:
        print("ERROR in teachers crawling")
        print(e)


def retrieve_teachers_pages(info, path):
    date = datetime.datetime.today().strftime('%Y%m%d')
    for item in info:
        try:
            position = item['position']
            url = item['url']
            filename = "{}_{}.html".format(position, date)
            get_html_teacher(url, path, filename)
        except:
            time.sleep(uniform(20, 30))
            position = item['position']
            url = item['url']
            filename = "{}_{}.html".format(position, date)
            get_html_teacher(url, path, filename)


def get_html_teacher(url, path, filename):
    Path(path).mkdir(parents=True, exist_ok=True)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0'),
                         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, os.path.join(path, filename))
    time.sleep(uniform(1, 2))


def store_teachers_info(info,
                        path,
                        filename):
    Path(path).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(path, filename), 'w') as fp:
        json.dump(info, fp)


def run_crawler(languages_url, crawling_size, storing_path, done=set([])):
    bot = create_chrome_bot()
    for language in languages_url:
        if language not in done:
            try:
                print('Crawling {}'.format(language))
                info = visit_language(bot, languages_url[language], language, crawl_size=crawling_size[language])
                if info:
                    store_teachers_info(info, storing_path + "teachers_list/" + language,
                                        datetime.datetime.today().strftime('%Y%m%d.json'))
                    retrieve_teachers_pages(info, storing_path + "teachers_html/" + language)
                    time.sleep(uniform(120, 180))
            except Exception as e:
                print(e)
                print("Error crawling {}".format(language))


def main():
    languges_of_interest = pd.read_csv("../../data/results/languages_to_explore.csv", index_col=0, sep=";")
    storing_path = "../../data/preply/"
    done = set([name for name in os.listdir("../../data/preply/teachers_list/")])

    # Transform number_italki
    languges_of_interest['number_preply'] = languges_of_interest['number_preply'].apply(
        lambda x: x if x <= 1000 else 1000)

    columns = ['language', 'number_preply', 'url_preply']

    languges_of_interest = languges_of_interest[columns]

    number_preply = dict(zip(languges_of_interest.language, languges_of_interest.number_preply))

    languages_to_crawl = dict(zip(languges_of_interest.language, languges_of_interest.url_preply))

    crawling_size = {}
    for lang in languages_to_crawl:
        crawling_size[lang] = min(number_preply[lang], 600)

    run_crawler(languages_to_crawl, crawling_size, storing_path, done=done)


if __name__ == "__main__":
    main()

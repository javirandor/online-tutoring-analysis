import requests
import json
import os
import urllib.request
import pandas as pd
from ast import literal_eval
import datetime
from pathlib import Path
import time
from crawlers.utils import get_url, create_chrome_bot
from random import uniform
from constants import DATA_PATH


def get_languages(bot):
    bot.get("https://www.verbling.com/find-teachers")

    time.sleep(uniform(1, 3))

    # Find "Teaches" menu and click on it
    try:
        element = bot.find_element_by_css_selector("div.FindTeacherFilter-teaches")
        element.click()
        time.sleep(uniform(1, 3))

        # Get all languages in the menu
        list_el = bot.find_elements_by_css_selector("div.FilterList-ItemNotSelectable")

        # For the available languages. Generate a languages with their name and indentifier for the query
        languages = {}
        for element in list_el:
            if element.text != 'Any language':  # Discard first any language element in the menu
                languages[element.text] = element.find_element_by_tag_name("img").get_attribute('language')

        return languages

    except:  # To avoid crawlers, they change the design and tags of the website
        element = bot.find_element_by_css_selector("div.sc-jzJRlG")
        element.click()
        time.sleep(uniform(1, 3))

        # Get all languages in the menu
        list_el = bot.find_elements_by_css_selector("div.sc-kpOJdX")

        # For the available languages. Generate a languages with their name and indentifier for the query
        languages = {}
        for element in list_el:
            if element.text != 'Any language':  # Discard first any language element in the menu
                languages[element.text] = element.find_element_by_tag_name("img").get_attribute('language')
        return languages

def generate_languages_url(languages, url_prefix):
    languages_url = {}

    for lang in languages:
        languages_url[lang] = url_prefix + "?language=" + languages[lang]

    return languages_url

def get_languages_json(path):
    with open(path) as f:
        languages_url = json.load(f)
    return languages_url

def visit_language(bot, url, crawl_size):
    get_url(bot, url)

    # Scroll until we get desired results
    teachers = bot.find_elements_by_css_selector("div.TeacherItem")

    while len(teachers) < crawl_size:
        prev_len = len(teachers)
        bot.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;")
        time.sleep(uniform(2, 4))
        teachers = bot.find_elements_by_css_selector("div.TeacherItem")
        if len(teachers) == prev_len:
            time.sleep(uniform(2, 4))
            bot.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;")
            time.sleep(uniform(2, 4))
            teachers = bot.find_elements_by_css_selector("div.TeacherItem")
            if len(teachers) == prev_len:
                break


    bot.execute_script("window.scrollTo(0, 0);var lenOfPage=document.body.scrollHeight;")
    time.sleep(uniform(1, 4))

    teachers_information = []
    position = 1

    for teacher in teachers:
        try:
            info = teacher.find_element_by_tag_name('a.ignore.link-reset')
            name = info.text
            url = info.get_attribute('href')

            try:
                teacher.find_element_by_tag_name('strong.teacher-featured')
                is_featured = True
            except:
                is_featured = False

            teachers_information.append(
                {'name': name, 'url': url, 'is_featured': is_featured, 'position': position,
                 'visited': datetime.datetime.today().strftime('%Y-%m-%d')})
            position = position + 1
        except:
            print('ERROR VERBLING CHANGED DESIGN :(')
            position = position + 1

    return teachers_information

def retrieve_teachers_pages(info, path):
    date = datetime.datetime.today().strftime('%Y%m%d')
    for item in info:
        position = item['position']
        url = item['url']
        filename = "{}_{}.html".format(position, date)
        get_html_teacher(url, path, filename)

def get_html_teacher(url, path, filename):
    Path(path).mkdir(parents=True, exist_ok=True)
    opener = urllib.request.build_opener()
    opener.addheaders = [('User-agent', 'Mozilla/5.0'), ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
    urllib.request.install_opener(opener)
    urllib.request.urlretrieve(url, os.path.join(path, filename))
    time.sleep(uniform(1,2))

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
                info = visit_language(bot, languages_url[language], crawl_size=1000)
                store_teachers_info(info, storing_path+"teachers_list/"+language, datetime.datetime.today().strftime('%Y%m%d.json'))
                retrieve_teachers_pages(info, storing_path+"teachers_html/"+language)
                time.sleep(uniform(5,10))
            except:
                print("Error crawling {}".format(language))


if __name__ == "__main__":

    languges_of_interest = pd.read_csv(os.path.join(DATA_PATH, "results/languages_to_explore.csv"), index_col=0, sep=";")
    storing_path = os.path.join(DATA_PATH, "verbling/")

    # Transform number_italki
    languges_of_interest['number_verbling'] = languges_of_interest['number_verbling'].apply(lambda x: x if x <= 1000 else 1000)

    columns = ['language', 'number_verbling', 'url_verbling']

    languges_of_interest = languges_of_interest[columns]

    number_verbling = dict(zip(languges_of_interest.language, languges_of_interest.number_verbling))

    languages_to_crawl = dict(zip(languges_of_interest.language, languges_of_interest.url_verbling))

    crawling_size = {}
    for lang in languages_to_crawl:
        crawling_size[lang] = number_verbling[lang]

    languages_info = run_crawler(languages_to_crawl, crawling_size, storing_path, done)
import requests
import json
import os
import urllib.request
import pandas as pd
from ast import literal_eval
import datetime
from pathlib import Path
import time
from math import ceil
from random import uniform
from constants import *


def get_languages():
    # Get code for each language
    url = "https://api.italki.com/api/v2/teacher/language"

    payload = {}
    headers = {}

    languages_codes = requests.request("GET", url, headers=headers, data=payload).json()
    languages_codes = languages_codes["data"]
    languages_codes = languages_codes['popular'] + languages_codes['other_language']

    # Get dictionary language name - code
    url = "https://translate.italki.com/i18n/en_us.json"

    mapping = requests.request("GET", url, headers=headers, data=payload).json()

    # Build languages information dictionary
    languages_info = {}

    for language in languages_codes:
        try:
            name = mapping[language]
            languages_info[name] = {}
            languages_info[name]['code'] = language
            languages_info[name]['url'] = "https://www.italki.com/teachers/" + language
        except:
            pass

    return languages_info


def get_teachers_info(language_id, api_url ="https://api.italki.com/api/v2/teachers", to_crawl=50):
    """
    Queries the API for teachers
    :return: JSON data containing conversations
    """
    try:
        if (to_crawl <= 100):
            print("Querying API for {} in page".format(language_id))
            payload = "{\"teach_language\":{\"language\":\"%s\"},\"page_size\":%s,\"user_timezone\":\"Europe/Madrid\"}" % (
            language_id, str(to_crawl))
            headers = {'Content-Type': 'application/json'}
            response = requests.request("POST", api_url, headers=headers, data=payload).json()
            return response['data']

        else:
            pages_number = ceil(to_crawl/20)
            crawled = 0
            data = []
            for page_number in range(1, pages_number+1):

                remaining = to_crawl-crawled

                if (remaining > 20):
                    page_size = 20
                else:
                    page_size=remaining

                print("Querying API for {} in page {}".format(language_id, page_number))
                payload = "{\"teach_language\":{\"language\":\"%s\"},\"page\":%s,\"page_size\":%s,\"user_timezone\":\"Europe/Madrid\"}" % (language_id, str(page_number), str(page_size))
                headers = {'Content-Type': 'application/json'}
                response = requests.request("POST", api_url, headers=headers, data=payload).json()
                data.append(response['data'])

                crawled += page_size

                time.sleep(uniform(0,2))

            return data

    except Exception as e:
        print("Error querying {}".format(language_id))
        print(e)
        return None

def store_info(info,
               path,
               filename):
    Path(path).mkdir(parents=True, exist_ok=True)
    with open(os.path.join(path, filename), 'w') as fp:
        json.dump(info, fp)

def run_crawler(languages, crawling_size):
    languages_info = get_languages()
    languages_filtered = {lang: languages_info[lang] for lang in languages}

    for language in languages_filtered:
        info = get_teachers_info(languages_filtered[language]['code'], to_crawl=crawling_size[language])
        if info:
            store_info(info, os.path.join(DATA_PATH, "italki/teachers/{}/".format(language)), datetime.date.today().strftime("%Y%m%d")+".json")
        time.sleep(3)


if __name__ == "__main__":
    languges_of_interest = pd.read_csv(os.path.join(DATA_PATH, "results/languages_to_explore.csv"), index_col=0, sep=";")
    languges_of_interest["max_teachers"] = languges_of_interest[["number_italki", "number_preply", "number_verbling"]].max(axis=1)

    # Transform number_italki
    languges_of_interest['number_italki'] = languges_of_interest['number_italki'].apply(lambda x: x if x <= 1000 else 1000)

    columns = ['language', 'max_teachers', 'number_italki', 'url_italki', 'languages_italki']

    number_italki_temp = dict(zip(languges_of_interest.languages_italki, languges_of_interest.number_italki))
    number_italki = {}
    for lang in number_italki_temp:
        number_italki[literal_eval(lang)[0]] = number_italki_temp[lang]

    language_mapping = dict(zip(languges_of_interest.language, languges_of_interest.languages_italki))
    for lang in language_mapping:
        language_mapping[lang] = literal_eval(language_mapping[lang])[0]

    languages_to_crawl = languges_of_interest['languages_italki'].tolist()
    languages_to_crawl = [literal_eval(sublist)[0] for sublist in languages_to_crawl]

    crawling_size = {}
    for lang in languages_to_crawl:
        crawling_size[lang] = number_italki[lang]

    languages_info = run_crawler(languages_to_crawl, crawling_size)
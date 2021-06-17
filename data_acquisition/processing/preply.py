import json
import time
from random import uniform
import pandas as pd
from processing.utils import infer_gender_image, infer_gender_name, download_images
import os
import re
from bs4 import BeautifulSoup
import pandas as pd
import requests
from constants import *
import urllib
from pathlib import Path
import datetime


def visit_language(list_path: str,
                   html_path: str,
                   language: str,
                   file_regex: str = "([0-9]+)\_([0-9]+)"):
    files = set([file for file in os.listdir(html_path + language) if ~file.startswith('.')])
    teachers = []

    # Read teachers lists
    list_files = set([file for file in os.listdir(list_path + language) if ~file.startswith('.')])
    lists = {}
    for l in list_files:
        lists[l.replace('.json', '')] = pd.read_json(os.path.join(list_path + language, l))

    for file in files:
        match = re.match(file_regex, file)
        pos = match.group(1)
        date = match.group(2)

        if date in lists:
            soup = generate_soup(os.path.join(html_path + language, file), pos, language, lists[date])

            if soup:
                info = crawl_teacher(pos, date, language, lists[date], soup)
                teachers.append(info)

    df = pd.DataFrame(teachers)
    return df


def generate_soup(file_path: str,
                  position: int,
                  language: str,
                  prior_info: dict):

    soup = BeautifulSoup(open(file_path), "html.parser")
    url = prior_info[prior_info['position'] == int(position)]['url'].values[0]
    if language.lower() in url:
        return None
    elif '?ssr=true' in url:
        url = url.replace('/?ssr=true', '')

    attempts = 0

    while soup.find("h2", {'class': 'name___10LsT'}) is None and attempts < 3:
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0'),
                             ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, file_path)
        soup = BeautifulSoup(open(file_path), "html.parser")
        time.sleep(uniform(1, 2))
        attempts += 1

    if soup.find("h2", {'class': 'name___10LsT'}) is None:
        return None
    else:
        return soup


def crawl_teacher_old(position: int,
                  date: int,
                  language: str,
                  prior_info: dict,
                  soup):
    info = {}

    info["language"] = language
    info["position"] = position
    info["retrieval_date"] = date
    info['is_featured'] = prior_info[prior_info['position'] == int(position)]['is_featured'].values[0]

    try:
        info["user_name"] = soup.find("span", {"class": "ecom-name"}).text.strip()
    except:
        info['user_name'] = 'ERROR'
    try:
        info["url"] = "https:" + soup.find("link", {"rel": "alternate"}).get('href')
    except:
        info['url'] = 'ERROR'
    try:
        info['nationality'] = soup.find("span", {"class": "hint"}).text.strip()
    except:
        info['nationality'] = 'ERROR'
    try:
        info['avg_rating'] = soup.find("span", {"class": "ts-tutor-rating--total"}).text.strip()
    except:
        if soup.find("div", {"class": "tutor-stats__item tutor-stats__item--new-tutor"}):
            info['avg_rating'] = 'NEW TUTOR'
        else:
            info['avg_rating'] = 'ERROR'
    try:
        info['num_ratings'] = soup.findAll("div", {"class": "box__title box__title--md"})[-1].text.split()[1]
    except:
        if soup.find("div", {"class": "tutor-stats__item tutor-stats__item--new-tutor"}):
            info['num_ratings'] = 'NEW TUTOR'
        else:
            info['num_ratings'] = 'ERROR'

    try:
        teaches = soup.findAll("div", {"class": "tabs__item"})
        info['teaches'] = [lang.text.strip() for lang in teaches if 'language' in lang.text]
    except:
        info['teaches'] = 'ERROR'

    try:
        subjects = soup.findAll("h6", {"class": "p-subjects__title"})
        if len(subjects):
            info['subjects'] = [s.text.strip() for s in subjects]
        else:
            info['subjects'] = None
    except:
        info['subjects'] = 'ERROR'

    try:
        speaks = {}
        for _ in soup.findAll("span", {"data-qa-group": "tutor-speaks-elements"}):
            l = _.text.split()
            speaks[l[0]] = l[1]

        info['speaks'] = speaks
    except:
        info['speaks'] = 'ERROR'

    try:
        lessons = soup.findAll("div", {"class": "list-icon__text"})

        for l in lessons:
            if len(l.text.split()) == 2:
                info['lessons'] = l.text.split()[0]
                break
    except:
        info['lessons'] = 'ERROR'

    try:
        info['price'] = soup.find("span", {"class": "tutor-price__value"}).text
    except:
        info['price'] = 'ERROR'

    try:
        info['price_currency'] = soup.find("span", {"class": "tutor-price__currency"}).text
    except:
        info['price_currency'] = 'ERROR'

    try:
        info['avatar_url'] = re.findall(r'(https?://[^\s\)\']+)',
                                    soup.find("div", {"class": "avatar avatar--profile avatar--square"}).get('style'))[0]
    except:
        info['avatar_url'] = 'ERROR'

    return info

def crawl_teacher(position: int,
                  date: int,
                  language: str,
                  prior_info: dict,
                  soup):
    info = {}

    info["language"] = language
    info["position"] = position
    info["retrieval_date"] = date
    info['is_featured'] = prior_info[prior_info['position'] == int(position)]['is_featured'].values[0]

    try:
        info["user_name"] = soup.find("h2", {'class': 'name___10LsT'}).text.strip()
    except:
        info['user_name'] = 'ERROR'
    try:
        info["url"] = soup.find("meta", {'property': 'og:url'}).get('content')
    except:
        info['url'] = 'ERROR'
    try:
        info['nationality'] = soup.find("img", {'class': 'flag___26DQj'}).get('alt')
    except:
        info['nationality'] = 'ERROR'
    try:
        info['avg_rating'] = soup.find("div", {'class': 'RatingIndicatorRating___374zP'}).text
    except:
        if soup.find("div", {"class": "NewTutorBadge___sVfwo"}):
            info['avg_rating'] = 'NEW TUTOR'
        else:
            info['avg_rating'] = 'ERROR'
    try:
        info['num_ratings'] = soup.find("div", {'class': 'ReviewsNumber___1enrU'}).text
    except:
        if soup.find("div", {"class": "NewTutorBadge___sVfwo"}):
            info['avg_rating'] = 'NEW TUTOR'
        else:
            info['avg_rating'] = 'ERROR'

    try:
        teaches = soup.findAll("a", {"class": "item___2xHv5"})
        info['teaches'] = [lang.text.strip() for lang in teaches if 'language' in lang.text]
        if len(info['teaches']) == 0:
            teaches = soup.findAll("li", {"class": "item___2xHv5"})
            info['teaches'] = [lang.text.strip() for lang in teaches if 'language' in lang.text]

            if len(info['teaches']) == 0:
                info['teaches'] = None
    except:
        info['teaches'] = 'ERROR'

    try:
        subjects = soup.findAll("h5", {"class": "bold___1WVGs"})
        if len(subjects):
            info['subjects'] = [s.text.strip().replace('blank', '') for s in subjects]
        else:
            info['subjects'] = None
    except:
        info['subjects'] = 'ERROR'

    try:
        speaks = {}
        for s in soup.findAll("li", {"class": "item___18Wix"}):
            level = s.find('span').text
            lang = s.text.replace(level, '')
            speaks[lang] = level

        info['speaks'] = speaks
    except:
        info['speaks'] = 'ERROR'

    try:
        info['lessons'] = soup.find("span", {'class': 'totalLessons___1m96F'}).text
    except:
        info['lessons'] = 'ERROR'

    try:
        price = soup.find("div", {'class': 'PriceIndicatorPrice___w9jW1'}).text.split()
        info['price'] = price[0]
        info['price_currency'] = price[1]
    except:
        info['price'] = 'ERROR'

    try:
        info['avatar_url'] = soup.find("img", {'class': 'AvatarImg___2dRk2 AvatarImgLoaded___1em79'}).get('src')
    except:
        info['avatar_url'] = 'ERROR'

    return info


def obtain_teachers_info(teachers, crawler):
    teacher_info = []
    for teacher in teachers:
        teacher_info.append(crawl_teacher(teacher, crawler))
        time.sleep(uniform(2, 5))

    return teacher_info


def read_teachers(data_path):
    with open(data_path, "r") as read_file:
        teachers_dict = json.load(read_file)

    return teachers_dict


def infer_gender(df, column_name, prob_bound, img_url_col, images_path):
    df = infer_gender_name(df, column_name)
    df_not_ready = df[df['gender_name_prob'] <= prob_bound]

    images = list(df_not_ready[img_url_col].unique())
    download_images(images, images_path, delete_folder=True)
    img_gender = infer_gender_image(images_path)

    img_gender = img_gender.rename(columns={'image': 'avatar_url'})
    img_gender = img_gender.set_index('avatar_url')

    # Transform df for join
    df['avatar_url'] = df['avatar_url'].str.replace(
        'https://res.cloudinary.com/verbling/image/fetch/c_fill,f_png,f_auto,g_face,h_150,w_150/', '')

    result = df.join(img_gender, on='avatar_url', how='left')
    return result

def map_nationality(df):
    codes = pd.read_csv(country_codes_path)
    df = df.rename(columns={'nationality': 'nationality_full'})
    df = pd.merge(df, codes, how='left', left_on='nationality_full', right_on='Name')
    df = df.drop(columns='Name').rename(columns={'Code': 'nationality'})
    df[df['nationality'].isnull()][['nationality', 'nationality_full']].drop_duplicates().to_csv('/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/wrong_codes.csv', mode='a', header=False)
    return df


def main():
    list_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/preply/teachers_list/"
    html_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/preply/teachers_html/"
    output_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/preply/results/"

    languages = set([lang for lang in os.listdir(list_path) if not lang.startswith('.')])
    done = set([name for name in os.listdir("../../data/preply/results/")])

    for language in languages-done:
        df = visit_language(list_path, html_path, language)
        Path(os.path.join(output_path, language)).mkdir(parents=True, exist_ok=True)
        df = map_nationality(df)
        df.to_csv(output_path+language+"/{}.csv".format(datetime.datetime.today().strftime('%Y%m%d')))

if __name__ == "__main__":
    main()
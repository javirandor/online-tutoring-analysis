import pandas as pd
from processing.utils import infer_gender_image, infer_gender_name, download_images, consolidate_gender, clean_name
import os
import re
from bs4 import BeautifulSoup
import datetime
from pathlib import Path
import json

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
    return soup

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

    script = str([s for s in soup.find_all('script') if str(s).endswith('var isMobile = false;</script>')][0])

    json_details = json.loads(re.findall("var apolloState = (.*)", script)[0][:-1])

    teacher_key = [key for key in list(json_details.keys()) if key.startswith('Teacher')][0]
    user_key = [key for key in list(json_details.keys()) if key.startswith('User')][0]

    teacher_info = json_details[teacher_key]

    try:
        info["first_name"] = json_details[user_key]['first_name']
    except:
        info['first_name'] = 'ERROR'

    try:
        info["last_name"] = json_details[user_key]['last_name']
    except:
        info['last_name'] = 'ERROR'

    try:
        info["url"] = soup.findAll('link', {'rel': 'alternate'})[0].get('href')
    except:
        info['url'] = 'ERROR'
    try:
        if 'nationality' in teacher_info.keys():
            info['nationality'] = teacher_info['nationality']
        else:
            info['nationality'] = teacher_info['country']
    except:
        info['nationality'] = 'ERROR'

    try:
        info['location'] = json_details[user_key]['timezone']
    except:
        info['location'] = 'ERROR'

    try:
        info['avg_rating'] = teacher_info['avg_rating']
    except:
        info['avg_rating'] = 'ERROR'

    try:
        info['avg_lessons_per_students'] = teacher_info['avg_lessons_per_students']
    except:
        info['avg_lessons_per_students'] = 'ERROR'

    try:
        info['num_ratings'] = teacher_info['num_ratings']
    except:
        info['num_ratings'] = 'ERROR'

    try:
        info['teaching_levels'] = teacher_info['teaches_levels']['json']
    except:
        info['teaching_levels'] = 'ERROR'

    try:
        info['teaches'] = language
    except:
        info['teaches'] = 'ERROR'

    try:
        skill_keys = [key for key in list(json_details.keys()) if 'Skill' in key]
        class_details = []

        for key in skill_keys:
            class_details.append({'category': json_details[key]['category'], 'name': json_details[key]['name']})

        info['class_details'] = class_details

    except:
        info['class_details'] = "ERROR"

    try:
        langs = soup.findAll('span', {'class': 'ProfLanguage'})
        speaks = {}
        for s in langs:
            lang_code = re.findall("<span language=\"([\w]+)\"", str(s))[0]
            lang = re.findall("<span language=\"\w+\">([\w]+)<", str(s))[0]
            level = re.findall("<div class=.*>([\w]+)", str(s))[0]
            speaks[lang] = {'code': lang_code, 'level': level}

        info['speaks'] = speaks

    except:
        info['speaks'] = 'ERROR'

    try:
        info['lessons'] = json_details[teacher_info['user']['id']]['num_past_tutor_sessions_teacher']
    except:
        info['lessons'] = 'ERROR'

    try:
        info['students'] = json_details[teacher_key]['num_students']
    except:
        info['students'] = 'ERROR'

    try:
        price_keys = [key for key in list(json_details.keys()) if 'prices' in key][:-1]
        prices = []

        for key in price_keys:
            num_lessons = json_details[key]['num_lessons']
            prices.append({'num_lessons': num_lessons, 'price': float(json_details[key]['price_cents'])/100})

        info['price_detail'] = prices
        info['price'] = prices[0]['price']/prices[0]['num_lessons']
    except:
        info['price'] = 'ERROR'

    try:
        dialect_key = [key for key in list(json_details.keys()) if 'AccentDialect' in key]
        if len(dialect_key):
            info['dialect'] = json_details[dialect_key]['id']['name']
        else:
            info['dialect'] = 'Undefined'
    except:
        info['dialect'] = 'ERROR'


    info['price_currency'] = 'USD'

    try:
        info['avatar_url'] = json_details[user_key]['profile_pic_url']
    except:
        info['avatar_url'] = 'ERROR'

    return info

def main():
    list_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/preply/teachers_list/"
    html_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/preply/teachers_html/"
    output_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/preply/results/"

    languages = set([lang for lang in os.listdir(list_path) if ~lang.startswith('.')])

    for language in languages:
        df = visit_language(list_path, html_path, language)
        df.to_csv(output_path+language+"/{}.csv".format(datetime.datetime.today().strftime('%Y%m%d')))

def infer_gender(df, column_name, prob_bound, img_url_col, images_path):
    df = infer_gender_name(df, column_name)
    df_not_ready = df[df['gender_name_prob'] <= prob_bound]

    images = list(df_not_ready[img_url_col].unique())
    download_images(images, images_path, delete_folder=True)
    img_gender = infer_gender_image(images_path)

    img_gender = img_gender.rename(columns={'image': 'avatar_url'})
    img_gender = img_gender.set_index('avatar_url')

    #Transform df for join
    df['avatar_url'] = df['avatar_url'].str.replace('https://res.cloudinary.com/verbling/image/fetch/c_fill,f_png,f_auto,g_face,h_150,w_150/', '')

    result = df.join(img_gender, on='avatar_url', how='left')
    return result

if __name__ == "__main__":
    list_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/verbling/teachers_list/"
    html_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/verbling/teachers_html/"
    output_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/verbling/results/"

    languages = set([lang for lang in os.listdir(list_path) if lang!='.DS_Store'])

    for language in languages:
        df = visit_language(list_path, html_path, language)
        Path(output_path+language).mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path+language+"/{}.csv".format(datetime.datetime.today().strftime('%Y%m%d')))

    """
    path = "/Users/javirando/Desktop/Universidad/TFG/online-tutoring-analysis/data/verbling/verbling_teachers_english_50_03092020.json"
    data_path = "/Users/javirando/Desktop/Universidad/TFG/online-tutoring-analysis/data/verbling/"
    img_path = data_path + "images/avatar/"

    teachers = read_teachers(path)

    bot = create_chrome_bot()
    teachers_info = obtain_teachers_info(teachers, bot)

    df = pd.DataFrame(teachers_info)

    df = clean_name(df, "user_name", "user_name_clean", ['teacher', 'IELTS', '|'])

    df_gender = infer_gender(df, "user_name_clean", 0.75, "avatar_url", img_path)

    df_gender = consolidate_gender(df=df_gender, gender_img_column='gender_img', gender_name_column='gender_name', gender_name_prob='gender_name_prob', prob_bound=0.75)

    index = 1
    df_gender.to_csv("/Users/javirando/Desktop/Universidad/TFG/online-tutoring-analysis/data/rankings/verbling_english_{}.csv".format(index))
    """
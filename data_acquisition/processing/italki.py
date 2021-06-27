import pandas as pd
import os
import json
from processing.utils import infer_gender_image, infer_gender_name, download_images, consolidate_gender
from pathlib import Path
import datetime
from constants import *


def read_data(data_path: str, language: str):
    data_files = [f for f in os.listdir(data_path) if not f.startswith('.')]
    teachers = []

    for file in data_files:
        f = open(os.path.join(data_path, file))
        json_data = json.load(f)
        retrieval_date = file.replace('.json', '')
        if type(json_data[0]) is list:
            json_data = [item for sublist in json_data for item in sublist]

        for i in range(len(json_data)):
            teacher_info = json_data[i]
            temp = {}
            temp['position'] = i + 1
            temp['language'] = language
            temp['retrieval_date'] = retrieval_date
            temp['user_id'] = teacher_info['user_info']['user_id']
            temp['user_name'] = teacher_info['user_info']['nickname']
            temp['avatar_file_name'] = teacher_info['user_info']['avatar_file_name']
            temp['video_picture'] = teacher_info['teacher_info']['qiniu_video_pic_url']
            temp['is_pro'] = teacher_info['user_info']['is_pro']
            temp['origin_country'] = teacher_info['user_info']['origin_country_id']
            temp['teaches'] = teacher_info['teacher_info']['teach_language']
            temp['also_speaks'] = teacher_info['teacher_info']['also_speak']
            temp['in_platform_since'] = teacher_info['teacher_info']['first_valid_time']
            temp['rating'] = teacher_info['teacher_info']['overall_rating']
            temp['number_sessions'] = teacher_info['teacher_info']['session_count']
            temp['price'] = teacher_info['course_info']['min_price']
            temp['price_time'] = 'hour'
            temp['price_currency'] = 'USD'
            teachers.append(temp)

    return pd.DataFrame(teachers)

def build_image_url(df, image_id_column):
    df['image_url'] = "https://imagesavatar-static01.italki.com/" + df[image_id_column] + "_Avatar.jpg"
    return df


def main():
    data_path = DATA_PATH + "italki/teachers/"
    output_path = DATA_PATH + "italki/results/"

    languages = set([lang for lang in os.listdir(data_path) if not lang.startswith('.')])
    done = set([name for name in os.listdir(output_path)])

    for language in languages-done:
        df = read_data(data_path+language, language)
        Path(os.path.join(output_path, language)).mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path+language+"/{}.csv".format(datetime.datetime.today().strftime('%Y%m%d')))


if __name__ == "__main__":

    main()
import pandas as pd
import os
import json
from processing.utils import infer_gender_image, infer_gender_name, download_images, consolidate_gender
from pathlib import Path
import datetime


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
    data_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/italki/teachers/"
    output_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/italki/results/"

    languages = set([lang for lang in os.listdir(data_path) if not lang.startswith('.')])
    done = set([name for name in os.listdir(output_path)])

    for language in languages-done:
        df = read_data(data_path+language, language)
        Path(os.path.join(output_path, language)).mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path+language+"/{}.csv".format(datetime.datetime.today().strftime('%Y%m%d')))


if __name__ == "__main__":

    main()

    """
    data_path = "/Users/javirando/Desktop/Universidad/TFG/online-tutoring-analysis/data/italki/"
    img_path = data_path+"images/avatar/"
    teachers_file_prefix='italki_teachers'

    # Read json data
    data = read_data(data_path, teachers_file_prefix)

    # Transform data into pandas
    dfs = json_to_pandas(data)

    i = 1
    for df in dfs:
        # Build image url
        df = build_image_url(df, "avatar_file_name")

        # Infer gender
        df_gender = infer_gender(df=df, column_name='user_name', prob_bound=0.75, images_path=img_path)

        # Consolidate gender
        df_gender = consolidate_gender(df=df_gender, gender_img_column='gender_img', gender_name_column='gender_name', gender_name_prob='gender_name_prob', prob_bound=0.75)

        df_gender.to_csv("/Users/javirando/Desktop/Universidad/TFG/online-tutoring-analysis/data/results/italki_english_{}.csv".format(i))

        i = i+1
        """

import pandas as pd
import requests
import shutil
import os
#from deepface import DeepFace
#from genderize import Genderize
from constants import *

def clean_name(df, name_column, new_column, remove_list):
    # Lowercase everything
    df[new_column] = df[name_column].str.lower()
    remove_list = [x.lower() for x in remove_list]

    # Remove undesired words
    df[new_column] = df[new_column].str.replace('|'.join(remove_list), '')

    # Get only name
    df[new_column] = df[new_column].str.split().str[0]

    # Title case names
    df[new_column] = df[new_column].str.title()
    return df

def infer_gender_name(df, column_name):
    unique_names = list(df[column_name].unique())
    guess = Genderize().get(unique_names)

    # Create dataframe from guesses
    guess_df = pd.DataFrame(guess)
    guess_df = guess_df.rename(columns={'name': column_name, 'gender': 'gender_name', 'probability': 'gender_name_prob'})
    guess_df = guess_df[[column_name, 'gender_name', 'gender_name_prob']]

    # Merge results
    result = df.join(guess_df.set_index(column_name), on=[column_name], how='left')

    return result

def download_images(images_urls, store_path, delete_folder: bool = False):
    # Source: https://towardsdatascience.com/how-to-download-an-image-using-python-38a75cfa21c

    if not os.path.exists(store_path):
        os.makedirs(store_path)
    elif delete_folder:
        shutil.rmtree(store_path)
        os.makedirs(store_path)

    for url in images_urls:
        filename = store_path + url.split("/")[-1]

        # Open the url image, set stream to True, this will return the stream content.
        r = requests.get(url, stream=True)

        # Check if the image was retrieved successfully
        if r.status_code == 200:
            # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
            r.raw.decode_content = True

            # Open a local file with wb ( write binary ) permission.
            with open(filename, 'wb') as f:
                shutil.copyfileobj(r.raw, f)

            print('Image sucessfully Downloaded: ', filename)
        else:
            print('Image Couldn\'t be retreived')


def infer_gender_image(images_path):
    images = os.listdir(images_path)

    demographies = DeepFace.analyze([images_path + i for i in images], actions=['gender'], enforce_detection=False)

    df = pd.DataFrame.from_dict(demographies, orient='index')

    df = df.reset_index()

    df['index'] = images

    df = df.rename(columns={'index': 'image', 'gender': 'gender_img'})

    df['gender_img'] = df['gender_img'].str.replace('Man', 'male')
    df['gender_img'] = df['gender_img'].str.replace('Woman', 'female')

    return df


def consolidate_gender(df, gender_img_column, gender_name_column, gender_name_prob, prob_bound):
    def unify_columns(gender_name, gender_img, gender_prob):
        if not gender_name:
            if gender_img:
                return gender_img
            else:
                return GENDER_ERROR
        else:
            if (not gender_img and float(gender_prob)>prob_bound) or gender_name == gender_img:
                return gender_name
            else:
                return GENDER_ERROR

    df = df.where(pd.notnull(df), None)
    df['gender'] = df.apply(lambda x: unify_columns(x[gender_name_column], x[gender_img_column], x[gender_name_prob]), axis=1)
    return df
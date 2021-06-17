from constants import *
import os
import json
import pandas as pd
import requests
from pathlib import Path

def clean_name(df, name_column, new_column, remove_list):
    # Lowercase everything
    df[new_column] = df[name_column].str.lower()
    remove_list = [x.lower() for x in remove_list]

    # Remove undesired words
    #df[new_column] = df[new_column].str.replace('|'.join(remove_list), '')

    # Get only name
    #df[new_column] = df[new_column].str.split().str[0]

    # Title case names
    df[new_column] = df[new_column].str.title()
    return df

def query_gender_api(name, nationality):
    url = "https://gender-api.com/v2/gender"
    if len(name) < 3:
        name = name+"{}".format("".join([" " for i in range(3-len(name))]))

    payload = "{\"full_name\": \"%s\", \"country\": \"%s\"}" % (name, nationality)
    headers = {
        'Authorization': 'Bearer {}'.format(api_key),
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload.encode('utf-8'))

    response = json.loads(response.content)

    try:
        return response['gender'], response['probability'], response['details']['samples'], response['details']['first_name_sanitized']
    except:
        return "Unknown", None, None, None

def query_genderize_api(name, nationality):
    query = "https://api.genderize.io/?name={0}&country_id={1}".format(name, nationality)
    if api_key:
        query += "&apikey={}".format(api_key)
    r = requests.get(query)
    r.raise_for_status()
    response = json.loads(str(r.text))
    return response['gender'], response['probability'], response['count']

def gender_name(df, nationality_col, names_df, name_col='clean_name'):

    df_temp = df
    df_temp['first_name'] = df_temp[name_col].str.split().str.get(0)
    df_previous = pd.merge(df_temp, names_df, left_on=['first_name', nationality_col], right_on=['sanitized_name', 'nationality'], how='left')
    df_known = df_previous[~df_previous['gender'].isnull()]
    df_unknown = df_previous[df_previous['gender'].isnull()]
    df_unknown['gender'], df_unknown['probability'], df_unknown['count'], df_unknown['sanitized_name'] = zip(*df_unknown.apply(lambda x: query_gender_api(x[name_col], x[nationality_col]), axis=1))

    df_unknown['sanitized_name'] = df_unknown['sanitized_name'].str.capitalize()

    names_df = names_df.append(df_unknown[['sanitized_name', 'nationality', 'gender', 'probability', 'count']]).reset_index(drop=True)
    names_df = names_df.drop_duplicates()

    return df_known.append(df_unknown), names_df

def genderize_dataframe(path,
                        names_df,
                        name_col,
                        nationality_col):

    df = pd.read_csv(path, index_col=0)
    df = clean_name(df, name_col, "clean_name", remove_list)

    if "origin_country" in df.columns:
        df = df.rename(columns={'origin_country': 'nationality'})

    unique_df = df[['clean_name', nationality_col]].drop_duplicates()

    genders, names_df = gender_name(unique_df, names_df=names_df, nationality_col=nationality_col, name_col='clean_name')

    result = pd.merge(df, genders, how='left')

    return result, names_df


def main(platform):
    data_path = platforms[platform]['results_path']
    name_col = platforms[platform]['name_col']
    nationality_col = platforms[platform]['nationality_col']
    gender_path = platforms[platform]['gender_path']

    try:
        names_df = pd.read_csv(names_df_path, sep=';', index_col=0)
    except:
        names_df = pd.DataFrame(columns=['sanitized_name', 'nationality', 'gender', 'probability', 'count'])

    languages = set([lang for lang in os.listdir(data_path) if not lang.startswith('.')])
    done = set([name for name in os.listdir(gender_path)])

    for language in languages - done:
        print("Genderizing {}".format(language))
        for file in os.listdir(os.path.join(data_path, language)):
            if file.startswith('.'):
                pass
            df, names_df = genderize_dataframe(os.path.join(data_path, language, file), names_df, name_col, nationality_col)
            Path(os.path.join(gender_path, language)).mkdir(parents=True, exist_ok=True)
            df.to_csv(gender_path + language + "/{}".format(file))
            names_df.to_csv(names_df_path, sep=';')

if __name__ == "__main__":
    main('preply')
    main('italki')
    main('verbling')
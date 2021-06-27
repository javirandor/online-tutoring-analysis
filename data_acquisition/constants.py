CHROME_DRIVER_PATH = "../chromedriver"
DATA_PATH = "" # Finish with /

GENDER_ERROR = "GENDER_ERROR"
platforms = {
    'preply': {'results_path': '',
               'gender_path': '',
               'name_col': 'user_name',
               'nationality_col': 'nationality'},
    'verbling': {'results_path': '',
                 'gender_path': '',
                 'name_col': 'first_name',
                 'nationality_col': 'nationality'},
    'italki': {'results_path': '',
               'gender_path': '',
               'name_col': 'user_name',
               'nationality_col': 'nationality'}
}

names_df_path = DATA_PATH + "names_df.csv"
country_codes_path = DATA_PATH + "countries_codes.csv"
remove_list = ['IELTS', 'TOEFL', 'CAE', 'Dr.', 'Mr.', 'Ms.', 'Mrs.', 'D.']

api_key = "" # Introduce your GENDER API key


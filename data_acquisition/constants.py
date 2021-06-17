CHROME_DRIVER_PATH = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/production/chromedriver"
GENDER_ERROR = "GENDER_ERROR"
platforms = {
    'preply': {'results_path': '/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/preply/results/',
               'gender_path': '/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/preply/gender/',
               'name_col': 'user_name',
               'nationality_col': 'nationality'},
    'verbling': {'results_path': '/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/verbling/results/',
                 'gender_path': '/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/verbling/gender/',
                 'name_col': 'first_name',
                 'nationality_col': 'nationality'},
    'italki': {'results_path': '/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/italki/results/',
               'gender_path': '/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/italki/gender/',
               'name_col': 'user_name',
               'nationality_col': 'nationality'}
}
names_df_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/names_df.csv"
country_codes_path = "/Users/javi/Desktop/Universidad/TFG/online-tutoring-analysis/data/countries_codes.csv"
remove_list = ['IELTS', 'TOEFL', 'CAE', 'Dr.', 'Mr.', 'Ms.', 'Mrs.', 'D.']
api_key = "bbd4154c33e079d676da4d3a15cae8a94c3915b332e2ecacae561f5f99ef6b15"


from selenium import webdriver
from constants import CHROME_DRIVER_PATH

def create_chrome_bot():
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito --lang=en")
    options.add_experimental_option('prefs', {'intl.accept_languages': 'en,en_US'})
    options.add_experimental_option("excludeSwitches", ["disable-popup-blocking"])

    return webdriver.Chrome(CHROME_DRIVER_PATH, options=options)

def get_url(bot, url):
    """
    Navigate to an URL. Assures it starts with https

    :param url:
    :return:
    """
    if url.startswith("http") is False:
        url = "https://" + url

    bot.get(url)
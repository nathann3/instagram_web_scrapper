import os
import time

from selenium.webdriver import Firefox

from instagram_scraper.scraper.scraper import Scraper
from instagram_scraper.scraper.create_df import Create_DataFrame


class CheckEnv:

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, '_' + self.name)

    def __set__(self, instance, value):
        if value is None:
            try:
                value = os.environ["INSTA_%s" % self.name.upper()]
            except KeyError:
                value = None
        setattr(instance, '_' + self.name, value)

    def __set_name__(self, owner, name):
        self.name = name

class Posts:

    scrape = Scraper()
    df = Create_DataFrame()
    user = CheckEnv()
    password = CheckEnv()

    def __init__(self, term, n=9, user=None, password=None):
        self.user = user
        self.password = password
        self.browser = Firefox()
        self.scrape = {'post_urls': self.get_post_urls(term, n), 'browser': self.browser}
        self.df = self.scrape

    def get_post_urls(self, term, n):
        url = user_or_tag(term)
        if self.user and self.password:
            login(self.browser, self.user, self.password)
        self.browser.get(url)
        post_links = []
        while len(post_links) < n:
            lis = self.browser.find_elements_by_tag_name('a')
            for web_element in lis:
                href = web_element.get_attribute('href')
                if 'https://www.instagram.com/p/' in href and href not in post_links:
                    post_links.append(href)
            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
            self.browser.execute_script(scroll_down)
            time.sleep(5)
        posts = post_links[:n]
        return posts

class Users:
    scrape = Scraper()
    user = CheckEnv()
    password = CheckEnv()

    def __init__(self, term, user=None, password=None):
        self.user = user
        self.password = password
        self.browser = Firefox()
        if self.user and self.password:
            login(self.browser, self.user, self.password)
        self.scrape = {'post_urls': self.get_user_urls(term), 'browser': self.browser}


    def get_user_urls(self, users):
        urls = []
        if isinstance(users, list):
            for user in users:
                url = "https://www.instagram.com/" + user
                urls.append(url)
        else:
            url = "https://www.instagram.com/" + users
            urls.append(url)
        return urls


def user_or_tag(term):
    if term.startswith("#"):
        term = term.lstrip('#')
        url = 'https://www.instagram.com/explore/tags/%s' % (term)
    else:
        url = "https://www.instagram.com/%s" % (term)
    return url

def login(browser, user, password):
    browser.get('https://www.instagram.com/')
    time.sleep(2)
    fields = browser.find_elements_by_tag_name('input')
    fields[0].send_keys(user)
    time.sleep(0.5)
    fields[1].send_keys(password)
    time.sleep(0.5)
    login_button = '/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[4]/button'
    browser.find_element_by_xpath(login_button).click()
    time.sleep(6)

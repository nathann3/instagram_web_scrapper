import os
import time

from selenium.webdriver import Firefox

from instagram_scraper.scraper.scraper import Scraper
from instagram_scraper.scraper.create_df import Create_DataFrame


class CheckEnv:
    """Checks .env file for Instagram credentials"""
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
    """Scapes Instagram Posts information and returns them as dynamically created attributes."""

    # handles scraping of information as well as setting them as attributes
    scrape = Scraper()

    # handles creation of DataFrame
    df = Create_DataFrame()

    # checks .env for credentials
    user = CheckEnv()
    password = CheckEnv()

    def __init__(self, term, n=9, user=None, password=None):
        self.user = user
        self.password = password
        self.browser = Firefox()
        self.scrape = {'post_urls': self.get_post_urls(term, n), 'browser': self.browser}
        self.df = self.scrape

    def get_post_urls(self, term, n):
        """
        Retrieves urls of Instagram posts based on hashtag or username
        :param term: hashtag or username
        :param n: number of posts to be scraped
        :return: list of post urls
        """

        # gives appropriate url based on term
        url = user_or_tag(term)

        # logs in if credentials are provided
        if self.user and self.password:
            login(self.browser, self.user, self.password)
        self.browser.get(url)
        post_links = []

        # appends to post url until number of posts specified
        while len(post_links) < n:

            # gathers all links on webpage
            lis = self.browser.find_elements_by_tag_name('a')
            for web_element in lis:
                href = web_element.get_attribute('href')

                # checks if links are Instagram posts and prevent repeat posts
                if 'https://www.instagram.com/p/' in href and href not in post_links:
                    post_links.append(href)

            # scrolls down to retrieve more posts
            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
            self.browser.execute_script(scroll_down)

            # sleeps to prevent being banned
            time.sleep(3)
        posts = post_links[:n]
        return posts

class Users:
    """Scapes Instagramers' account information and returns them as dynamically created attributes."""

    # handles scraping of information as well as setting them as attributes
    scrape = Scraper()

    # handles creation of DataFrame
    df = Create_DataFrame()

    # checks .env for credentials
    user = CheckEnv()
    password = CheckEnv()

    def __init__(self, term, user=None, password=None):
        self.user = user
        self.password = password
        self.browser = Firefox()
        if self.user and self.password:
            login(self.browser, self.user, self.password)
        self.scrape = {'post_urls': self.get_user_urls(term), 'browser': self.browser}
        self.df = self.scrape


    def get_user_urls(self, users):
        """
        Retrieves urls of Instagram users' accounts
        :param users: user or list of users
        :return: list of Instagram account urls
        """

        # handles if single user or list of users are passed
        if isinstance(users, list):
            urls = ["https://www.instagram.com/" + user for user in users]
        else:
            urls = ["https://www.instagram.com/" + users]
        return urls


def user_or_tag(term):
    """
    chooses appropriate url depending on term
    :param term: hashtag or username
    :return: url
    """
    if term.startswith("#"):
        term = term.lstrip('#')

        # url for hashtags
        url = 'https://www.instagram.com/explore/tags/%s' % (term)
    else:

        # url for users
        url = "https://www.instagram.com/%s" % (term)
    return url

def login(browser, user, password):
    """
    logs into Instagram with provided credentials
    :param browser: selenium webdriver
    :param user: Instagram username
    :param password: Instagram password
    :return: None
    """
    browser.get('https://www.instagram.com/')
    time.sleep(2)
    fields = browser.find_elements_by_tag_name('input')

    # inputs username credential
    fields[0].send_keys(user)
    time.sleep(0.5)

    # inputs password credential
    fields[1].send_keys(password)
    time.sleep(0.5)
    login_button = '/html/body/div[1]/section/main/article/div[2]/div[1]/div/form/div[4]/button'

    # clicks login button
    browser.find_element_by_xpath(login_button).click()

    # sleep to prevent being banned and give some time for login request
    time.sleep(6)

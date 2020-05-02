import time
import urllib.request
import io
import pandas as pd

from PIL import Image
from selenium.webdriver import Firefox

from .scrapper import Scrapper
from .create_df import Create_DataFrame



class Posts():
    scrape = Scrapper()
    df = Create_DataFrame()

    def __init__(self, term, n=9, user=None, password=None):
        self.term = term
        self.n = n
        self.user = user
        self.password = password
        self.dumb = self.get_post_urls(term)
        self.post_urls = self.dumb['posts']
        self.browser = self.dumb['browser']
        self.scrape = {'post_urls': self.post_urls, 'browser': self.browser, "user": user, "password": password}
        self.df = self.scrape

    def get_post_urls(self, term):
        print('this ran')
        if term.startswith("#"):
            term = term.lstrip('#')
            url = 'https://www.instagram.com/explore/tags/%s' % (term)
        else:
            url = "https://www.instagram.com/%s" % (term)
        browser = Firefox()
        if self.user:
            self.login(browser, self.user, self.password)
        browser.get(url)
        post_links = []
        while len(post_links) < self.n:
            lis = browser.find_elements_by_tag_name('a')
            for web_element in lis:
                if 'https://www.instagram.com/p' in web_element.get_attribute('href'):
                    post_links.append(web_element.get_attribute('href'))
            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
            browser.execute_script(scroll_down)
            time.sleep(5)
        posts = post_links[:self.n]
        return {'posts': posts, 'browser': browser}

    def login(self, browser, user, password):
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
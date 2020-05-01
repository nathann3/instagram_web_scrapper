import urllib.request
import io
import pandas as pd

from PIL import Image
from selenium.webdriver import Firefox

from .scrapper import Scrapper
from .create_df import Create_DataFrame



class Posts:

    scrape = Scrapper()
    df = Create_DataFrame()

    def __init__(self, tag, n=9):
        self.tag = tag
        self.n = n
        self.post_urls = self.get_post_urls(tag, n)
        self.scrape = self.post_urls
        self.df = self.scrape

    def get_post_urls(self, tag, n):
        tag = self.tag
        n = self.n
        browser = Firefox()
        browser.get('https://www.instagram.com/explore/tags/%s' % (tag))
        lis = browser.find_elements_by_tag_name('a')
        post_links = []
        for web_element in lis:
            if 'https://www.instagram.com/p' in web_element.get_attribute('href'):
                post_links.append(web_element.get_attribute('href'))
        top_posts = post_links[:n]
        browser.quit()
        return top_posts

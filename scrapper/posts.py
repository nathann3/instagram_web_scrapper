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

    def __init__(self, term, n=9):
        self.term = term
        self.n = n
        self.post_urls = self.get_post_urls(term)
        self.scrape = self.post_urls
        self.df = self.scrape

    def get_post_urls(self, term):
        if term.startswith("#"):
            term = term.lstrip('#')
            url = 'https://www.instagram.com/explore/tags/%s' % (term)
        else:
            url = "https://www.instagram.com/%s" % (term)
        browser = Firefox()
        browser.get(url)
        post_links = []
        while len(post_links) < self.n:
            lis = browser.find_elements_by_tag_name('a')
            for web_element in lis:
                if 'https://www.instagram.com/p' in web_element.get_attribute('href'):
                    post_links.append(web_element.get_attribute('href'))
            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
            browser.execute_script(scroll_down)
            time.sleep(10)
        posts = post_links[:self.n]
        browser.quit()
        return posts

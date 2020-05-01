import urllib.request
import io
import pandas as pd

from selenium.webdriver import Firefox
from .scrapper import Scrapper
from PIL import Image


class Posts:

    scrape = Scrapper()

    def __init__(self, tag, n=9):
        self.tag = tag
        self.n = n
        self.post_urls = self.get_post_urls(tag, n)
        self.scrape = self.post_urls

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

    def create_df(self):
        data = self.scrape
        df = pd.DataFrame(data)
        df["datetime_posted"] = pd.to_datetime(df["datetime_posted"])
        df['hashtags'] = df['image_caption'].str.findall(r"#\w+")
        return df

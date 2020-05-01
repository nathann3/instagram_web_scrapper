import pandas as pd
import urllib.request
import io

from selenium.webdriver import Firefox
from PIL import Image


class Scraper:

    def __init__(self, tag, n=9):
        self.tag = tag
        self.n = n
        self.browser = Firefox()
        self.post_urls = self.get_post_urls(tag, n)
        self.meta = self.scrape()

    def get_post_urls(self, tag, n):
        tag = self.tag
        n = self.n
        self.browser.get('https://www.instagram.com/explore/tags/%s' % (tag))
        lis = self.browser.find_elements_by_tag_name('a')
        post_links = []
        for web_element in lis:
            if 'https://www.instagram.com/p' in web_element.get_attribute('href'):
                post_links.append(web_element.get_attribute('href'))
        top_posts = post_links[:n]
        return top_posts

    def get_image_urls(self):
        lis = self.browser.find_elements_by_tag_name('img')
        image_url = lis[1].get_attribute('src')
        return image_url

    def get_image(self, url_list):
        pictures_arrays = []
        for url in url_list:
            img = io.BytesIO(urllib.request.urlopen(url).read())
            image = Image.open(img)
            image.thumbnail((150, 150), Image.LANCZOS)
            pictures_arrays.append(image)
        return pictures_arrays

    def get_username(self):
        path = '/html/body/div[1]/section/main/div/div/article/header/div[2]/div[1]/div[1]/a'
        username = self.browser.find_element_by_xpath(path).text
        return username

    def get_post_likes(self):
        try:
            path = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/section[2]/div/div/button/span'
            likes = self.browser.find_element_by_xpath(path).text
        except:
            button_path = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/section[2]/div/span'
            self.browser.find_element_by_xpath(button_path).click()
            video_path = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/section[2]/div/div/div[4]/span'
            likes = self.browser.find_element_by_xpath(video_path).text
        return likes

    def scrape(self):
        time_list = []
        caption_list = []
        username_list = []
        likes_list = []
        image_urls_list = []
        for url in self.post_urls:
            self.browser.get(url)
            time_list.append(self.get_post_datetime())
            caption_list.append(self.get_post_captions())
            username_list.append(self.get_username())
            likes_list.append(self.get_post_likes())
            image_urls_list.append(self.get_image_urls())
        post_dict = {
                    'time': time_list,
                    'caption': caption_list,
                    'username': username_list,
                    'likes': likes_list,
                    'image_urls': image_urls_list
                    }
        self.browser.quit()
        return post_dict

    def get_post_datetime(self):
        # time is in UTC
        lis = self.browser.find_elements_by_tag_name('time')
        time = lis[0].get_attribute('datetime')
        return time

    def get_post_captions(self):
        path = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/div[1]/ul/div/li/div/div/div[2]/span'
        caption = self.browser.find_element_by_xpath(path).text
        return caption

    def create_df(self):
        data = {
            "post_url": self.post_urls,
            "image": self.get_image(self.meta['image_urls']),
            "image_url": self.meta['image_urls'],
            "username": self.meta['username'],
            "picture_caption": self.meta['caption'],
            "picture_likes": self.meta['likes'],
            "datetime_posted": self.meta['time']
        }
        df = pd.DataFrame(data)
        df["datetime_posted"] = pd.to_datetime(df["datetime_posted"])
        df['hashtags'] = df['picture_caption'].str.findall(r"#\w+")
        return df


def main():
    corg = Scraper('corgis', 10)
    df = corg.create_df()
    print(df)

if __name__ == "__main__":
    main()
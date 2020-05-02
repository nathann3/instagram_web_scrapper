import urllib.request
import io
import time

from selenium.webdriver import Firefox
from PIL import Image


class Scrapper:

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, '_' + self.name)

    def __set__(self, instance, value):
        val = self.scrape(value['post_urls'], user=value["user"], password=value["password"])
        setattr(instance, '_' + self.name, val)
        for key in val:
            setattr(instance, key, val[key])


    def __set_name__(self, owner, name):
        self.name = name

    # ------------------------------------------------------------------------------------------------

    def scrape(self, post_urls, user=None, password=None):
        time_list = []
        caption_list = []
        username_list = []
        likes_list = []
        image_urls_list = []
        image_list = []
        self.browser = Firefox()
        if user:
            self.login(self.browser, user, password)
        for url in post_urls:
            self.browser.get(url)
            time_list.append(self.get_post_datetime())
            caption_list.append(self.get_post_captions())
            username_list.append(self.get_username())
            likes_list.append(self.get_post_likes())
            image_urls_list.append(self.get_image_urls())
            image_list.append(self.get_image(self.get_image_urls()))
        post_dict = {
            'post_url': post_urls,
            'image': image_list,
            "datetime_posted": time_list,
            "caption": caption_list,
            'username': username_list,
            "likes": likes_list,
            'image_url': image_urls_list,
        }
        self.browser.quit()
        return post_dict

    def get_image_urls(self):
        lis = self.browser.find_elements_by_tag_name('img')
        image_url = lis[1].get_attribute('src')
        return image_url

    def get_username(self):
        path = '/html/body/div[1]/section/main/div/div/article/header/div[2]/div[1]/div[1]/a'
        username = self.browser.find_element_by_xpath(path).text
        return username

    def get_post_likes(self):
        try:
            path = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/section[2]/div/div/button/span'
            likes = self.browser.find_element_by_xpath(path).text
        except:
            try:
                button_path = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/section[2]/div/span'
                self.browser.find_element_by_xpath(button_path).click()
                video_path = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/section[2]/div/div/div[4]/span'
                likes = self.browser.find_element_by_xpath(video_path).text
            except:
                likes = "0"
        likes = int(likes.replace(',', ''))

        return likes

    def get_post_datetime(self):
        # time is in UTC
        lis = self.browser.find_elements_by_tag_name('time')
        time = lis[0].get_attribute('datetime')
        return time

    def get_post_captions(self):
        try:
            path = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/div[1]/ul/div/li/div/div/div[2]/span'
            caption = self.browser.find_element_by_xpath(path).text
        except:
            return ''
        return caption

    def get_image(self, url):
        request = urllib.request.urlopen(url).read()
        img = io.BytesIO(request)
        image = Image.open(img)
        image.thumbnail((150, 150), Image.LANCZOS)
        return image

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

import urllib.request
import io
import time

from PIL import Image
from selenium.common.exceptions import NoSuchElementException


class Scraper:
    """Descriptor that scrapes information from Instagram and returns dynamically created attributes"""

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, "_" + self.name)

    def __set__(self, instance, value):
        val = self.scrape(value["post_urls"], value["browser"])
        setattr(instance, "_" + self.name, val)
        for key in val:
            setattr(instance, key, val[key])

    def __set_name__(self, owner, name):
        self.name = name

    # ------------------------------------------------------------------------------------------------

    def scrape(self, post_urls, browser):
        """
        Scrapes Instagram using provided browser and returns information as dict
        :param post_urls: list of urls to be scraped
        :param browser: selenium webdriver
        :return: dictionary containing scraped information
        """
        time_list = []
        caption_list = []
        username_list = []
        likes_list = []
        image_urls_list = []
        image_list = []
        posts_number_list = []
        self.browser = browser

        # for posts
        if post_urls[0].startswith("https://www.instagram.com/p/"):
            for url in post_urls:
                self.browser.get(url)
                time_list.append(self.get_post_datetime())
                caption_list.append(self.get_post_captions())
                username_list.append(self.get_username())
                likes_list.append(self.get_post_likes())
                image_urls_list.append(self.get_image_urls())
                image_list.append(self.get_image(self.get_image_urls()))
                time.sleep(2)
            post_dict = {
                "post_url": post_urls,
                "image": image_list,
                "datetime_posted": time_list,
                "caption": caption_list,
                "username": username_list,
                "likes": likes_list,
                "image_url": image_urls_list,
            }

        # for users
        elif post_urls[0].startswith("https://www.instagram.com/"):
            followers_list = []
            following_list = []
            for url in post_urls:
                self.browser.get(url)
                username_list.append(self.get_username())
                posts_number_list.append(self.get_posts_number())
                followers_list.append(self.get_followers())
                following_list.append(self.get_following())
                time.sleep(2)
            post_dict = {
                "user": username_list,
                "posts": posts_number_list,
                "followers": followers_list,
                "following": following_list,
            }
        self.browser.quit()
        return post_dict

    def get_image_urls(self):
        lis = self.browser.find_elements_by_tag_name("img")
        image_url = lis[1].get_attribute("src")
        return image_url

    def get_username(self):
        if self.browser.current_url.startswith("https://www.instagram.com/p/"):
            path = "/html/body/div[1]/section/main/div/div/article/header/div[2]/div[1]/div[1]/a"
        else:
            path = "/html/body/div[1]/section/main/div/header/section/div[1]/h2"
        username = self.browser.find_element_by_xpath(path).text
        return username

    def get_post_likes(self):
        try:
            path = "/html/body/div[1]/section/main/div/div[1]/article/div[2]/section[2]/div/div/button/span"
            likes = self.browser.find_element_by_xpath(path).text
        except:
            try:
                button_path = "/html/body/div[1]/section/main/div/div[1]/article/div[2]/section[2]/div/span"
                self.browser.find_element_by_xpath(button_path).click()
                video_path = "/html/body/div[1]/section/main/div/div[1]/article/div[2]/section[2]/div/div/div[4]/span"
                likes = self.browser.find_element_by_xpath(video_path).text
            except:
                likes = "0"
        likes = int(likes.replace(",", ""))

        return likes

    def get_post_datetime(self):
        # time is in UTC
        lis = self.browser.find_elements_by_tag_name("time")
        time = lis[0].get_attribute("datetime")
        return time

    def get_post_captions(self):
        try:
            path = "/html/body/div[1]/section/main/div/div[1]/article/div[2]/div[1]/ul/div/li/div/div/div[2]/span"
            caption = self.browser.find_element_by_xpath(path).text
        except:
            return ""
        return caption

    def get_image(self, url):
        request = urllib.request.urlopen(url).read()
        img = io.BytesIO(request)
        image = Image.open(img)
        image.thumbnail((100, 100), Image.LANCZOS)
        return image

    def get_posts_number(self):
        try:
            path = (
                "/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span"
            )
            posts = self.browser.find_element_by_xpath(path).text
        except NoSuchElementException:
            path = "/html/body/div[1]/section/main/div/header/section/ul/li[1]/a/span"
            posts = self.browser.find_element_by_xpath(path).text
        return posts

    def get_followers(self):
        path = "/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span"
        followers = self.browser.find_element_by_xpath(path).get_attribute("title")
        return followers

    def get_following(self):
        path = "/html/body/div[1]/section/main/div/header/section/ul/li[3]/a/span"
        following = self.browser.find_element_by_xpath(path).text
        return following

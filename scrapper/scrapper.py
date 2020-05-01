from selenium.webdriver import Firefox

class Scrapper:

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return getattr(instance, '_' + self.name)

    def __set__(self, instance, value):
        val = self.scrape(value)
        return setattr(instance, '_' + self.name, val)

    def __set_name__(self, owner, name):
        self.name = name

    # ------------------------------------------------------------------------------------------------

    def scrape(self, post_urls):
        time_list = []
        caption_list = []
        username_list = []
        likes_list = []
        image_urls_list = []
        self.browser = Firefox()
        for url in post_urls:
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
            'image_urls': image_urls_list,
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

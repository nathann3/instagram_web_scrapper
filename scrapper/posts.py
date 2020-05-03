import time

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
        self.browser = Firefox()
        self.post_urls = self.get_post_urls(term)
        self.scrape = {'post_urls': self.post_urls, 'browser': self.browser, "user": user, "password": password}
        self.df = self.scrape

    def get_post_urls(self, term):
        if term.startswith("#"):
            term = term.lstrip('#')
            url = 'https://www.instagram.com/explore/tags/%s' % (term)
        else:
            url = "https://www.instagram.com/%s" % (term)
        if self.user:
            self.login(self.browser, self.user, self.password)
        self.browser.get(url)
        post_links = []
        while len(post_links) < self.n:
            lis = self.browser.find_elements_by_tag_name('a')
            for web_element in lis:
                href = web_element.get_attribute('href')
                if 'https://www.instagram.com/p' in href and href not in post_links:
                    post_links.append(href)
            scroll_down = "window.scrollTo(0, document.body.scrollHeight);"
            self.browser.execute_script(scroll_down)
            time.sleep(5)
        posts = post_links[:self.n]
        return posts

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

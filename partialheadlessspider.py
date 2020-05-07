"""
Spider making a partial use of a Headless Browser

We use it to login in a page.

Then we save the cookies and use them in the following requests
"""

import time
from scrapy import Spider
from scrapy import Request
from firefoxheadless import FirefoxHeadless


DUMMY_URL = 'file:///etc/hosts'
LOGIN_URL = 'http://www.fakewebsite.com/login/'


class FakeSpider(Spider):
    name = 'fakewebsite.com'
    allowed_domains = ['fakewebsite.com']
    start_urls = ['http://www.fakewebsite.com/']

    login_usr = 'myusername'
    login_pwd = 'mypassword'

    def start_requests(self):
        self.login()
        for url in self.start_urls:
            # Please take a look at the `cookies` parameter, we are using our session cookies here
            yield Request(url, cookies=self.session_cookies)

    def login(self):
        # Please notice the `user_agent` parameter. Usually the websites use that
        # value too as part of the session identification
        # It's the same for the IP, in case you're using a proxy
        with FirefoxHeadless(user_agent=self.settings.get('USER_AGENT')) as browser:
            browser.get(LOGIN_URL)
            username_input = browser.driver.find_element_by_id('login')
            password_input = browser.driver.find_element_by_id('password')
            login_button = browser.driver.find_element_by_id('connect_button')

            username_input.send_keys(self.login_usr)
            password_input.send_keys(self.login_pwd)
            login_button.click()
            time.sleep(30)
            # Save the cookies
            self.session_cookies = browser.driver.get_cookies()

    def parse(self, response):
        '''We can start crawling the website always with the session cookies in our requests'''

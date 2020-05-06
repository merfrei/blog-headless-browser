"""
Basic solution to wrap Firefox Headless using Selenium driver
"""

import logging
import time
from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxProfile
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import WebDriverException


BINARY_PATH = '/usr/bin/firefox'
DRIVER_PATH = '/usr/bin/geckodriver'
DEFAULT_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0'


class FirefoxHeadless:
    '''Firefox Headless Browser using Selenium'''

    def __init__(self, *args, **kwargs):
        self.driver = FirefoxHeadless.create_driver(*args, **kwargs)

    def __enter__(self):
        '''Make a new browser instance and return it'''
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        '''The browser is closed at the end'''
        if exc_type is not None:
            logging.error('An error ocurred: %r : %r : %r', exc_type, exc_value, traceback)
        self.close()

    def get(self, url, sleep=5, retry=4):
        '''Get a page'''
        its_done = False
        error = None
        while not its_done and retry:
            try:
                self.driver.get(url)
                time.sleep(sleep)
            except WebDriverException as wd_exc:
                retry -= 1
                error = wd_exc
            else:
                its_done = True
        if not its_done and error is not None:
            raise error
        if not its_done:
            raise Exception('Could not get {}, an error has occurred'.format(url))

    def close(self):
        '''Close the browser. Driver quit'''
        self.driver.quit()

    @staticmethod
    def set_profile_proxy(profile, proxy):
        '''Given a proxy it will set it to use it in the current profile'''
        proxy_host, proxy_port = proxy.split(':')
        profile.set_preference('network.proxy.type', 1)
        profile.set_preference('network.proxy.http', proxy_host)
        profile.set_preference('network.proxy.http_port', int(proxy_port))
        profile.set_preference('network.proxy.ssl', proxy_host)
        profile.set_preference('network.proxy.ssl_port', int(proxy_port))
        profile.set_preference('network.proxy.ftp', proxy_host)
        profile.set_preference('network.proxy.ftp_port', int(proxy_port))
        profile.set_preference('network.proxy.socks', proxy_host)
        profile.set_preference('network.proxy.socks_port', int(proxy_port))

    @staticmethod
    def set_recommended_proxy_settings(profile):
        '''Set some recommended settings to use with proxies'''
        profile.set_preference('network.proxy.share_proxy_settings', True)
        profile.set_preference('network.proxy.backup.ssl', '')
        profile.set_preference('network.proxy.backup.ssl_port', 0)
        profile.set_preference('network.proxy.backup.socks', '')
        profile.set_preference('network.proxy.backup.socks_port', 0)
        profile.set_preference('network.proxy.backup.ftp', '')
        profile.set_preference('network.proxy.backup.ftp_port', 0)
        profile.set_preference('network.proxy.autoconfig_url', '')
        profile.set_preference('network.proxy.autoconfig_url.include_path', False)
        profile.set_preference('network.proxy.autoconfig_retry_interval_max', 300)
        profile.set_preference('network.proxy.autoconfig_retry_interval_min', 5)
        profile.set_preference('network.proxy.socks_version', 5)
        profile.set_preference('network.proxy.no_proxies_on', 'localhost, 127.0.0.1')
        profile.set_preference('network.proxy.failover_timeout', 1800)
        profile.set_preference('network.proxy.proxy_over_tls', True)
        profile.set_preference('network.proxy.socks_remote_dns', False)
        profile.set_preference('media.peerconnection.identity.enabled', False)
        profile.set_preference('media.peerconnection.identity.timeout', 1)
        profile.set_preference('media.peerconnection.turn.disable', True)
        profile.set_preference('media.peerconnection.use_document_iceservers', False)
        profile.set_preference('media.peerconnection.video.enabled', False)
        profile.set_preference('privacy.donottrackheader.enabled', True)
        profile.set_preference('privacy.trackingprotection.enabled', True)

    @classmethod
    def create_driver(cls, user_agent=None, proxy=None, download_dir='/tmp'):
        '''Create the driver using some custom settings'''
        options = Options()
        options.add_argument('-headless')

        profile = FirefoxProfile()

        if user_agent is not None:
            profile.set_preference('general.useragent.override', user_agent)
        else:
            profile.set_preference('general.useragent.override', DEFAULT_AGENT)

        profile.set_preference('browser.download.folderList', 2) # custom location
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', download_dir)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk',
                               ('text/plain, application/vnd.ms-excel, '
                                'text/csv, text/comma-separated-values, '
                                'application/octet-stream, '
                                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,'
                                ' application/pdf'))

        if proxy is not None:
            cls.set_profile_proxy(profile, proxy)
            cls.set_recommended_proxy_settings(profile)

        profile.update_preferences()

        driver = Firefox(profile,
                         firefox_binary=BINARY_PATH,
                         executable_path=DRIVER_PATH,
                         firefox_options=options)

        driver.set_window_size(1920, 1080)

        max_wait = 180
        driver.set_page_load_timeout(max_wait)
        driver.set_script_timeout(max_wait)

        return driver

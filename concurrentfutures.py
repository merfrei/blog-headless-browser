"""
Concurrent Headless Browser Using Futures
"""

import sys
import logging
import pprint
from concurrent import futures
from lxml import html as lxml_html
from firefoxheadless import FirefoxHeadless


HOMEPAGE_URL = 'https://www.nytimes.com/'
LOG_FORMAT = '%(levelname)s: %(asctime)s %(filename)s: %(message)s'


class NoArticlesFoundError(Exception):
    '''When no articles found'''


def crawl_nytimes_article(article_no=1):
    '''Go to the NY Times homepage and extract the N article body'''
    logging.info('Crawling article No. %d', article_no)
    with FirefoxHeadless() as browser:
        browser.get(HOMEPAGE_URL)
        article_links = browser.driver.find_elements_by_css_selector('article a')
        if len(article_links) < article_no:
            raise NoArticlesFoundError('No articles found for "{0:d}"'.format(article_no))
        link_src = article_links[article_no - 1].get_attribute('href')
        browser.get(link_src)
        html_sel = lxml_html.fromstring(browser.driver.page_source)
    logging.info('DONE: Article No. %d', article_no)
    return ' '.join(
        html_sel.xpath('//div[contains(@class, "StoryBodyCompanionColumn")]//text()')).strip()


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('Started')

    printer = pprint.PrettyPrinter(indent=2)
    with futures.ThreadPoolExecutor(4) as executor:
        res = executor.map(crawl_nytimes_article, list(range(1, 5)))
    printer.pprint(list(res))

    logging.info('Finished')

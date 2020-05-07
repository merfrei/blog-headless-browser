"""
Concurrent Headless Browser Using Pyppeteer with Asyncio
"""

import sys
import logging
import pprint
import asyncio
from w3lib.url import urljoin
from lxml import html as lxml_html
from pyppeteerbrowser import Browser


HOMEPAGE_URL = 'https://www.nytimes.com/'
LOG_FORMAT = '%(levelname)s: %(asctime)s %(filename)s: %(message)s'
TIMEOUT = 30 * 1000


class NoArticlesFoundError(Exception):
    '''When no articles found'''


async def get_html_body(browser, url):
    '''Given a browser and a URL it will return the HTML body as a string'''
    response = await browser.page.goto(url, timeout=TIMEOUT)
    return await response.text()


async def get_homepage_body():
    '''Goes to the homepage and returns the HTML'''
    logging.info('Going to homepage: %s', HOMEPAGE_URL)
    async with Browser('default') as browser:
        html_body = await get_html_body(browser, HOMEPAGE_URL)
    return html_body


async def crawl_nytimes_article(article_no, results_list):
    '''Go to the NY Times homepage and extract the N article body'''
    logging.info('Crawling article No. %d', article_no)
    homepage_html = await get_homepage_body()
    html_sel = lxml_html.fromstring(homepage_html)
    article_links = html_sel.xpath('//article//a/@href')
    if len(article_links) < article_no:
        raise NoArticlesFoundError('No articles found for "{0:d}"'.format(article_no))
    async with Browser('default') as browser:
        article_url = urljoin(HOMEPAGE_URL, article_links[article_no - 1])
        logging.info('Article %d URL: %s', article_no, article_url)
        html_body = await get_html_body(browser, article_url)
        html_sel = lxml_html.fromstring(html_body)
    logging.info('DONE: Article No. %d', article_no)
    results_list.append(' '.join(
        html_sel.xpath('//div[contains(@class, "StoryBodyCompanionColumn")]//text()')).strip())


if __name__ == '__main__':
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format=LOG_FORMAT, datefmt='%Y-%m-%d %H:%M:%S')
    logging.info('Started')

    printer = pprint.PrettyPrinter(indent=2)

    loop = asyncio.get_event_loop()
    results = []
    tasks = asyncio.gather(*[crawl_nytimes_article(art_no, results)
                             for art_no in range(1, 5)])
    loop.run_until_complete(tasks)
    printer.pprint(list(results))
    logging.info('Finished')

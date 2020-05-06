"""
A simple crawl using only a headless browser
"""

from lxml import html as lxml_html
from firefoxheadless import FirefoxHeadless


HOMEPAGE_URL = 'https://www.nytimes.com/'


def crawl_nytimes_first_article(browser):
    '''Go to the NY Times homepage and extract the first article body'''
    browser.get(HOMEPAGE_URL)
    article_link = browser.driver.find_element_by_css_selector('article')
    article_link.click()
    html_sel = lxml_html.fromstring(browser.driver.page_source)
    return ' '.join(
        html_sel.xpath('//div[contains(@class, "StoryBodyCompanionColumn")]//text()')).strip()


if __name__ == '__main__':
    with FirefoxHeadless() as browser:
        print(crawl_nytimes_first_article(browser))

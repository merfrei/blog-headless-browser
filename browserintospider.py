"""
Example of spider using a headless browser

WARNING:

It consumes a lot of resources, it's just an example.
Try to not use this in a real situation.

Also the results could not be correct, it's not the purpose of this example
You should see how I'm using a browser into a Scrapy spider.

From here, you can take this and develop your own OPTIMIZED spider using a headless browser.

"""

import csv

from scrapy import Spider
from scrapy import Selector
from scrapy import Request

from scrapy.item import Item
from scrapy.item import Field
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose
from scrapy.loader.processors import TakeFirst

from scrapy.crawler import CrawlerProcess

from firefoxheadless import FirefoxHeadless


OUTPUT_CSV = 'articles.csv'
DUMMY_URL = 'file:///etc/hosts'


class ExportCsvPipeline:

    def process_item(self, item, spider):
        self.writer.writerow(item)
        return item

    def open_spider(self, spider):
        self.file = open(OUTPUT_CSV, 'w')
        self.writer = csv.DictWriter(self.file, ['title', 'body'])
        self.writer.writeheader()

    def close_spider(self, spider):
        self.file.close()


class Loader(ItemLoader):
    default_input_processor = MapCompose(lambda x: x.strip())
    default_output_processor = TakeFirst()


class Article(Item):
    title = Field()
    body = Field()


class NYTimeSpider(Spider):
    name = 'nytimes.com'
    allowed_domains = ['nytimes.com']
    start_urls = ['https://www.nytimes.com/']

    def parse(self, response):
        article_urls = response.css('article a::attr(href)').extract()
        # Only the first three articles. It's just a example
        for url in article_urls[:3]:
            yield Request(DUMMY_URL, meta={'url': response.urljoin(url)},
                          callback=self.parse_article,
                          dont_filter=True)

    def parse_article(self, response):
        article_url = response.meta['url']
        with FirefoxHeadless(user_agent=self.settings.get('USER_AGENT')) as browser:
            browser.get(article_url)
            sel = Selector(text=browser.driver.page_source)
            title = sel.css('[itemprop="headline"]::text').get()
            body = ''.join(sel.css('[itemprop="articleBody"]').xpath('.//text()').extract())
            loader = Loader(item=Article(), selector=sel)
            loader.add_value('title', title)
            loader.add_value('body', body)
            yield loader.load_item()


if __name__ == "__main__":
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:77.0) Gecko/20190101 Firefox/77.0',
        'ITEM_PIPELINES': {'browserintospider.ExportCsvPipeline': 600},
    })

    process.crawl(NYTimeSpider)
    process.start()

import scrapy

from scrapy.loader import ItemLoader
from ..items import BankbpsplItem
from itemloaders.processors import TakeFirst


class BankbpsplSpider(scrapy.Spider):
	name = 'bankbpspl'
	start_urls = ['https://www.bankbps.pl/o-banku/aktualnosci']

	def parse(self, response):
		post_links = response.xpath('//div[@class="content_news"]')
		for post in post_links:
			url = post.xpath('./a/@href').get()
			date = post.xpath('./span[@class="news_date"]/text()').get()
			yield response.follow(url, self.parse_post, cb_kwargs={"date": date})

		next_page = response.xpath('//a[text()="Następna"]/@href').getall()
		yield from response.follow_all(next_page, self.parse)

	def parse_post(self, response, date):
		title = response.xpath('//h2/text()').get()
		description = response.xpath('//div[@id="sq_news_body" or @id="sq_news_summary"]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=BankbpsplItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()

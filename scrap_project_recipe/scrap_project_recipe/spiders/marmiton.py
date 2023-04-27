import scrapy


class MarmitonSpider(scrapy.Spider):
    name = "marmiton"
    allowed_domains = ["www.marmiton.org"]
    start_urls = ["http://www.marmiton.org/"]

    def parse(self, response):
        pass

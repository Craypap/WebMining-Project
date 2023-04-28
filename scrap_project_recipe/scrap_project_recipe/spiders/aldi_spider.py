from pathlib import Path

import scrapy

class AldiSpider(scrapy.Spider):
    # Nom du scraper
    name = 'aldi'

    def start_requests(self):
        start_urls = ['https://www.aldi-now.ch/fr/nouveau-dans-la-boutique-en-ligne?ipp=72&page=1#']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse_categories)

    # récupérer les catégories
    def parse_categories(self, response):
        categories = response.css('.js-catalog__trigger::attr(data-url)').getall()
        for category in categories:
            category_url = response.urljoin(category)
            yield scrapy.Request(url=category_url, callback=self.parse)

    def parse(self, response):
        # récupérer toutes les divs avec la classe recipe-card
        cards = response.css('.product-item.product-item--catalog')

        # pour chaque article
        for item in cards:
            sale_volume = item.css('.product-item__sale-volume::text').get().strip()
            weight, price_per_unit = sale_volume.split('\n')

            yield {
                'name': item.css('.product-item__name::text').get().strip(),
                'weight': weight.strip(),
                'price_per_unit': price_per_unit.strip(),
                'price': item.css('.money-price__amount::text').get().strip()
            }
        #changer de page
        next_page = response.css('.pagination__step--next::attr(href)').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, callback=self.parse)

# Copyright (c) 2023 Hofmann Florian
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = "Florian Hofmann"
__date__ = "27.04.2023"

import scrapy


class USPSpider(scrapy.Spider):
    """
    This class is the spider for the USP website
    """

    # name of the spider
    name = 'usp'

    def start_requests(self):
        start_urls = ['https://www.sbv-usp.ch/fr/prix/vente-directe/oeufs',
                      'https://www.sbv-usp.ch/fr/prix/vente-directe/viande-et-poisson',
                      'https://www.sbv-usp.ch/fr/prix/vente-directe/produits-laitiers',
                      'https://www.sbv-usp.ch/fr/prix/vente-directe/legumes',
                      'https://www.sbv-usp.ch/fr/prix/vente-directe/cereales-et-fourrage',
                      'https://www.sbv-usp.ch/fr/prix/vente-directe/baies',
                      'https://www.sbv-usp.ch/fr/prix/vente-directe/fruits',
                      'https://www.sbv-usp.ch/fr/prix/vente-directe/fait-maison']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # go to the url of the recipe and extract the name, ingredients and preparation
    def parse(self, response):
        items = response.css('tbody tr')
        line: int = 0
        unit: str = ''
        isUnitUnique: bool = False
        for item in items:
            if line == 0:  # avoid header
                # check if the unit is unique
                price_col = str(item.css('th:last-child::text').get())
                if len(price_col.split('/')) == 2:
                    unit = price_col.split('/')[1].strip()
                    # check if the unit is not "unité" (fait maison page)
                    if unit != 'unité':
                        isUnitUnique = True
                line += 1
                continue
            # check for subhead
            try:
                if item.css('th:first-child::text').get().strip() != '':
                    continue
            except Exception:
                pass
            # check if the item is not a product
            if item.css('td:first-child::text').get().strip() == '':
                line = 0  # reset line counter for next section
                continue
            yield {
                'name': item.css('td:first-child::text').get().strip(),
                'quantity': unit if isUnitUnique else item.css('td:nth-child(2)::text').get(),
                'price': item.css('td:last-child::text').get(),
            }
            line += 1

from pathlib import Path

import scrapy

######################################################
# To scrap, run the following command in the terminal:
#       scrapy crawl quotes -O drinks.json
######################################################


#create class to scrape data
class QuotesSpider(scrapy.Spider):
    # name of the spider
    name = 'quotes'

    def start_requests(self):
        start_urls = ['https://www.1001cocktails.com/recettes/selection_short-drinks.aspx']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'is_it_first_search':True, 'should_explore_more':True})


    # go to the url of the recipe and extract the name, ingredients and preparation
    def parse(self, response):

        #get all the divs with class recipe-card
        cards = response.css('div.recipe-card')

        # for each drink
        for drink in cards:

            yield {
                'name': drink.css('h4.recipe-card__title::text').get(),
                'note': drink.css('span.recipe-card__rating__value::text').get(),
                'number_of_review': drink.css('span.mrtn-font-discret::text').get().split(' ')[1]
            }

        if response.meta['should_explore_more']:
            for nav_pages in response.css('nav.af-pagination'):
                for page in nav_pages.css('li'):

                    # continue if the current li has the class selected (it's the current page)
                    if page.css('li::attr(class)').get() == "selected":
                        continue

                    should_explore_more = False

                    # In case it's the first search, we want to go to the other "ten" pages. 
                    # Those are hidden so we need to check if they are or not. For the next search, we won't explore those.
                    # But If it's the current first search, we will tell in the meta parameter that we want to explore the other pages of the "ten" pages
                    if page.css('li::attr(style)').get() == "display: none;":
                        if response.meta['is_it_first_search'] == False:    
                            continue
                        else :
                            should_explore_more = True

                    # go the the next page
                    next_page = page.css('a::attr(href)').get()
                    next_page = response.urljoin(next_page)
                    yield scrapy.Request(next_page, callback=self.parse, meta={'is_it_first_search':False, 'should_explore_more':should_explore_more})
                    

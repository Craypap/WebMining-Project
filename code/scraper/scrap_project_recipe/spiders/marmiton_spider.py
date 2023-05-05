from pathlib import Path

import scrapy

######################################################
# To scrap, run the following command in the terminal:
#       scrapy crawl marmiton -O recipe_marmiton.json
######################################################


#create class to scrape data
class MarmitonSpider(scrapy.Spider):
    # name of the spider
    name = 'marmiton'

    def start_requests(self):
        start_urls = [['https://www.marmiton.org/recettes/index/categorie/entree/','Entree'],
                      ['https://www.marmiton.org/recettes/index/categorie/plat-principal/','Plat principal'],
                      ['https://www.marmiton.org/recettes/index/categorie/dessert/','Dessert'],
                      ['https://www.marmiton.org/recettes/index/categorie/aperitif-ou-buffet/','Aperitif'],
                      ['https://www.marmiton.org/recettes?type=boisson', 'Boisson']]
        for url, category in start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'is_it_first_search':True, 'should_explore_tens':True, 'should_explore_hundreds':True, 'category':category})

    def parse(self, response):

        # get the link of every cards and yield the recipes
        for link_cards in response.css('a.recipe-card-link::attr(href)').getall():
            yield response.follow(link_cards, self.parse_recipe, meta={'is_it_first_search':response.meta['is_it_first_search'], 'should_explore_tens':response.meta['should_explore_tens'], 'should_explore_hundreds':response.meta['should_explore_hundreds'], 'category': response.meta['category']})

        # get the link of the next pages
        for nav_pages in response.css('nav.af-pagination'):

            pages = nav_pages.css('li')

            # check if it's the first research and if it is, we check that the last page indicated is not a custom one saying it's the last page
            # if it's a page that we will meet again, we should remove it
            if response.meta['is_it_first_search'] == True:

                last_page = int(pages[-1].css('a::text').get())
                previous_to_last_page = int(pages[-2].css('a::text').get())
                previous_previous_to_last_page = int(pages[-3].css('a::text').get())

                # the page will be met again if not a multiple of 100 and has few cases where it can be a multiple of 10 and still be removed (90-100-110, 100-200-210, but not 20-30-40)
                if last_page % 100 != 0:
                    if ( (last_page % 10 == 0) & (last_page-previous_to_last_page == previous_to_last_page-previous_previous_to_last_page) & (last_page<100) ) == False:
                        pages = pages[:-1]

            for page in pages:

                # continue if the current li has the class selected (it's the current page)
                if page.css('li::attr(class)').get() == "selected":
                    continue

                should_explore_tens = False
                should_explore_hundreds = False

                # In case we want to go through more than the 10 current pages of the current tenth one, we go through the "voir plus" which are hidden (display:none) 
                # For the next search, we won't explore those.
                if page.css('li::attr(style)').get() == "display: none;":
                    # if both meta parameter are false, we don't want to explore the "voir plus"
                    if response.meta['should_explore_tens'] == False & response.meta['should_explore_hundreds'] == False:    
                        continue

                    # if both meta parameter are true, we want to explore the "voir plus" only if the page is a hundredth number
                    if response.meta['should_explore_hundreds'] == True & response.meta['should_explore_tens'] == True:
                        if int(page.css('a::text').get()) % 100 == 0:
                            should_explore_hundreds = True

                    # if only the meta parameter should_explore_tens is true, we want to explore the "voir plus" only if the page is a tenth number
                    elif response.meta['should_explore_hundreds'] == False :
                        # check if the text of a inside li is a hundredth number of page, if yes we skip it
                        if int(page.css('a::text').get()) % 100 == 0:
                            continue

                # go the the next page
                next_page = page.css('a::attr(href)').get()
                next_page = response.urljoin(next_page)
                yield scrapy.Request(next_page, callback=self.parse, meta={'is_it_first_search':False, 'should_explore_tens':should_explore_tens, 'should_explore_hundreds':should_explore_hundreds, 'category': response.meta['category']})

    # parse the recipe 
    def parse_recipe(self, response):

        # get the ingredients inside every cards
        cards = response.css('div.MuiGrid-root.MuiGrid-item.MuiGrid-grid-xs-3.MuiGrid-grid-sm-3')
        ingredients = []

        for card in cards:

            quantity = card.css('span.SHRD__sc-10plygc-0.epviYI::text').extract()
            for i in range(len(quantity)):
                if quantity[i] == "⁄":
                    quantity[i] = ''.join(card.css('sup::text').extract()) +"/" + ''.join(card.css('sub::text').extract())
            quantity = ' '.join(quantity)
            #remove multiple spaces
            quantity = quantity.replace("\xc2\xa0", " ")
            quantity = ' '.join(quantity.split()) 

            # check if the name has a preposition at the beginning
            name = card.css('span.SHRD__sc-10plygc-0.kWuxfa span::text').extract()
            if name[0] == "de " or name[0] == "d'":
                # join name without the first index
                name = ' '.join(name[1:])
            else:
                name = ' '.join(name)
            #remove multiple spaces
            name = name.replace("\xc2\xa0", " ")
            name = ' '.join(name.split()) 

            # check if the name has some useless comments from the cook like (yes, that much but it's for getting the best taste)
            if "(" in name or ")" in name :
                new_name = ''
                inside_parentheses = False
                for char in name:
                    if char == '(':
                        inside_parentheses = True
                    elif char == ')':
                        inside_parentheses = False
                    elif not inside_parentheses:
                        new_name += char
                # remove all extra white spaces      
                name = ' '.join(new_name.split())

            ingredient = {
                'name': name,
                'quantity': quantity
            }
            ingredients.append(ingredient)

            price_range = response.css('p.RCP__sc-1qnswg8-1.iDYkZP::text').getall()[2] #"Bon marcher", "Moyen", "Assez Cher"
            if price_range == "bon marché":
                price_range = "1"
            elif price_range == "moyen":
                price_range = "2"
            elif price_range == "assez cher":
                price_range = "3"

        yield {
                'name': response.css('h1.SHRD__sc-10plygc-0.itJBWW::text').get(),
                'category': response.meta['category'],
                'price_range': price_range,
                'servings_quantity': response.css('span.SHRD__sc-w4kph7-4.knYsyq::text').get(), #for how many people
                'ingredients': ingredients
        }




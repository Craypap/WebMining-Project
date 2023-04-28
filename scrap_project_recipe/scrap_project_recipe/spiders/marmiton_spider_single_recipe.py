from pathlib import Path

import scrapy

######################################################
# To scrap, run the following command in the terminal:
#       scrapy crawl marmiton_single_recipe -O marmiton_single_recipe.json
######################################################


#create class to scrape data
class MarmitonSpider(scrapy.Spider):
    # name of the spider
    name = 'marmiton_single_recipe'

    def start_requests(self):
        start_urls = ['https://www.marmiton.org/recettes/recette_mojito-cubain_80528.aspx', 'https://www.marmiton.org/recettes/recette_tarte-tatin-a-la-banane-epicee_36627.aspx' ,'https://www.marmiton.org/recettes/recette_simplissimes-croissants-a-la-creme-de-marrons_44245.aspx', 'https://www.marmiton.org/recettes/recette_gateau-royal-aux-noix_14103.aspx']
        for url in start_urls:
            yield scrapy.Request(url=url, callback=self.parse, meta={'is_it_first_search':True, 'should_explore_tens':True, 'should_explore_hundreds':True})

    # parse the recipe 
    def parse(self, response):

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
                'price_range': price_range,
                'servings_quantity': response.css('span.SHRD__sc-w4kph7-4.knYsyq::text').get(), #for how many people
                'ingredients': ingredients
        }



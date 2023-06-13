# Copyright (c) 2023 Anthony Gugler, Florian Hofmann and Jérémy Jordan
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

"""
File containing a indexer class for ElasticSearch
"""

__authors__ = "Anthony Gugler, Florian Hofmann, Jérémy Jordan"
__date__ = "26.05.2023"

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import NotFoundError
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)


class PriceAnalysis:
    def __init__(self, host='localhost', port=9200, scheme='http', user: str = 'user', password: str = 'password'):
        self.elastic = Elasticsearch(hosts=[{'host': host, 'port': port, 'scheme': scheme}],
                                     basic_auth=(user, password))

    def get_price_from_ingredient(self, ingredient_name, index_name):
        """
        Get the price of the ingredient from the elastic search index
        :param ingredient_name: string
        :param index_name: string
        :return: List of Dicts
        """
        # Prepare the search query
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"ingredient": ingredient_name}},
                        {"match": {"other_ingredients": ingredient_name}}
                    ]
                }
            }
        }

        res = self.elastic.search(index=index_name, body=query)

        # If no match found, return empty list
        if res['hits']['total']['value'] == 0:
            return []

        # Return all matches
        return [hit['_source'] for hit in res['hits']['hits']]

    def get_price_from_ingredient_aldi(self, ingredient_name, index_name):
        """
        Get the price of the ingredient from the elastic search index only from aldi
        :param ingredient_name: string
        :param index_name: string
        :return: List of Dicts
        """
        # Prepare the search query
        query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"name": ingredient_name}},
                        {"match": {"source": "ALDI"}}
                    ]
                }
            }
        }

        res = self.elastic.search(index=index_name, body=query)

        # If no match found, return empty list
        if res['hits']['total']['value'] == 0:
            return []

        # Return best match and all other matches
        return [res['hits']['hits'][0]['_source'], res['hits']['hits']]

    @staticmethod
    def parse_recipe_quantity(quantity_str: str) -> float:
        """
        Method to parse the quantity of a recipe ingredient into a kg quantity
        If return is , it mean that is an invariant and always purchase one time the product
        """

        PIECE_KG = 0.2  # Weigh to use when the quantity is in piece on there is no unit

        quantity_str = quantity_str.lower()
        quantity_str = quantity_str.strip()
        if quantity_str == "":
            return 0
        # split one time the quantity string
        quantity_list = quantity_str.split(' ', 1)

        # check if there is a unit in the quantity string
        if len(quantity_list) == 1:
            return float(quantity_list[0]) * PIECE_KG

        if quantity_list[1] == 'g':
            return float(quantity_list[0]) / 1000
        elif quantity_list[1] == 'kg':
            return float(quantity_list[0])
        elif quantity_list[1] == 'l':
            return float(quantity_list[0]) * 1.03
        elif quantity_list[1] == 'cl':
            return float(quantity_list[0]) * 0.01
        elif quantity_list[1] == 'ml':
            return float(quantity_list[0]) * 0.001
        elif quantity_list[1] == 'verres':
            return float(quantity_list[0]) * 0.2
        elif quantity_list[1] == 'petite tasse':
            return float(quantity_list[0]) * 0.1
        elif quantity_list[1] == 'cuillère':
            return float(quantity_list[0]) * 0.005
        else:
            return 0  # consider as invariant




    @staticmethod
    def get_price_by_quantity(quantity_str, price):
        """
        Calculate the price according to the quantity
        :param quantity_str: str
        :param price: Dict
        :return: float
        """
        quantity_str = quantity_str.lower()
        quantity = 0

        if 'g' in quantity_str:  # grams
            quantity = float(quantity_str.split()[0]) / 1000
        elif 'verres' in quantity_str:  # glasses
            quantity = float(quantity_str.split()[0]) * 0.2
        elif 'petite tasse' in quantity_str:  # small cup
            quantity = float(quantity_str.split()[0]) * 0.1
        elif quantity_str.isdigit():  # plain number
            quantity = float(quantity_str)

        if 'price_kg' in price:
            return quantity * price['price_kg']
        elif 'price' in price:
            return quantity * price['price']
        else:
            return 0

    def get_price_for_recipe(self, recipe_id, recipe_index='recipe_marmiton', price_index='items_ingredient'):
        # Get the recipe from the elastic search
        try:
            recipe = self.elastic.get(index=recipe_index, id=recipe_id)['_source']
        except NotFoundError:
            print(f'Recipe with ID {recipe_id} not found in the {recipe_index} index.')
            return

        total_cost_aldi = {
            'Price according to quantity': 0,
            'Direct price': 0,
            'Price per kg': 0
        }
        total_cost_usp = {
            'Price according to quantity': 0,
            'Direct price': 0,
            'Price per kg': 0
        }

        ingredient_prices = {}

        # Loop through ingredients
        for ingredient in recipe['ingredients']:

            prices = self.get_price_from_ingredient(ingredient['name'], price_index)

            # If the ingredient price is found
            for price in prices:
                source_ingredient_key = f"{price['source']}-{ingredient['name']}"
                if source_ingredient_key in ingredient_prices:
                    continue

                cost_kg = price.get('price_kg', 0)
                direct_price = price.get('price', 0)
                quantity_price = self.get_price_by_quantity(ingredient['quantity'], price)

                print(f'Source: {price["source"]}')
                print(f'Ingredient: {ingredient["name"]}')
                print(f'Price per kg: {cost_kg}')
                print(f'Direct price: {direct_price}')
                print(f'Price according to quantity: {quantity_price}')
                print('-' * 29)

                # Update the total
                if price["source"] == 'ALDI':
                    total_cost_aldi['Price according to quantity'] += quantity_price
                    total_cost_aldi['Direct price'] += direct_price if direct_price > 0 else 0
                    total_cost_aldi['Price per kg'] += cost_kg if cost_kg > 0 else 0
                elif price["source"] == 'USP':
                    total_cost_usp['Price according to quantity'] += quantity_price
                    total_cost_usp['Direct price'] += direct_price if direct_price > 0 else 0
                    total_cost_usp['Price per kg'] += cost_kg if cost_kg > 0 else 0

                ingredient_prices[source_ingredient_key] = True

        print(f'Total cost for ALDI:')
        for key, value in total_cost_aldi.items():
            print(f'{key}: {value}')
        print()
        print(f'Total cost for USP:')
        for key, value in total_cost_usp.items():
            print(f'{key}: {value}')

    def query_recipe(self, query: str, recipe_index: str = 'recipe_marmiton', price_index='items_ingredient'):
        # prepare the search query
        query = {
            "query": {
                "match": {
                    "name": query
                }
            }
        }
        # get the recipe from the elastic search
        res = self.elastic.search(index=recipe_index, body=query)
        # keep the best match
        best_match = res['hits']['hits'][0]['_source'] if res['hits']['total']['value'] > 0 else None
        # query each ingredient and keep the best match
        for i in range(len(best_match['ingredients'])):
            prices, others = self.get_price_from_ingredient_aldi(best_match['ingredients'][i]['name'], price_index)
            # keep 6 first results and add them to the return object
            others = others[:6]
            tmp: list = []
            for o in others:
                # check to have only Aldi results
                if o['_source']['source'] != 'ALDI':
                    continue
                # compute quantity price with price per kg
                item_quantity = prices['price'] / prices['price_kg']
                o['_source']['quantity'] = item_quantity
                tmp.append(o['_source'])
            best_match['ingredients'][i]['others'] = tmp
            # compute quantity price with price per kg
            item_quantity = prices['price']/prices['price_kg']
            # add to the return object
            best_match['ingredients'][i]['quantity_kg'] = self.parse_recipe_quantity(best_match['ingredients'][i]['quantity'])
            best_match['ingredients'][i]['match'] = prices
            best_match['ingredients'][i]['match']['quantity'] = item_quantity


        return best_match


if __name__ == "__main__":
    price_analysis = PriceAnalysis()
    price_analysis.get_price_for_recipe('161')

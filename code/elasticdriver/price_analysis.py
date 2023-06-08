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
    def __init__(self, host='localhost', port=9200, scheme='http', user: str='user', password: str='password'):
        self.elastic = Elasticsearch(hosts=[{'host': host, 'port': port, 'scheme': scheme}], basic_auth=(user, password))

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
                "match": {
                    "other_ingredients": ingredient_name
                }
            }
        }

        res = self.elastic.search(index=index_name, body=query)

        # If no match found, return empty list
        if res['hits']['total']['value'] == 0:
            return []

        # Return all matches
        return [hit['_source'] for hit in res['hits']['hits']]

    @staticmethod
    def get_price_by_quantity(quantity, price):
        """
        Calculate the price according to the quantity
        :param quantity: str
        :param price: Dict
        :return: float
        """
        # Check if the quantity has a unit
        if ' ' in quantity:
            # Parse quantity and convert to kg
            quantity_value, quantity_unit = quantity.split(' ', 1)
        else:
            # If no unit is provided
            quantity_value = quantity
            quantity_unit = 'kg'

        quantity_value = float(quantity_value)

        if quantity_unit.lower() in ['g', 'gram', 'grams']:
            quantity_value /= 1000
        elif quantity_unit.lower() in ['cl', 'centiliter', 'centiliters']:
            quantity_value /= 100
        elif quantity_unit.lower() in ['l', 'liter', 'liters']:
            quantity_value *= 1  # Already in kg equivalent
        else:  # Unit not recognized
            quantity_value = 0

        if 'price_kg' in price:
            return quantity_value * price['price_kg']
        elif 'price' in price:
            return quantity_value * price['price']
        else:
            return 0

    def get_price_for_recipe(self, recipe_id, recipe_index='recipe_marmiton', price_index='items_ingredient'):
        """
        Get the total cost of a recipe
        :param recipe_id: string
        :param recipe_index: string
        :param price_index: string
        :return: None
        """
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
                if ingredient['name'] in ingredient_prices:
                    continue  # Skip if ingredient seen
                cost_kg = price.get('price_kg', 0)
                direct_price = price.get('price', 0)
                quantity_price = self.get_price_by_quantity(ingredient['quantity'], price)

                print(f'Source: {price["source"]}')
                print(f'Ingredient: {ingredient["name"]}')
                print(f'Raw Price per kg: {cost_kg}')
                print(f'Raw Direct price: {direct_price}')
                print(f'Raw Price according to quantity: {quantity_price}')
                print('-' * 29)

                # Update the total cost for each source
                #todo adapter la calculation du prix
                if price["source"] == 'aldi':
                    total_cost_aldi['Price according to quantity'] += quantity_price
                    total_cost_aldi['Direct price'] += direct_price
                    total_cost_aldi['Price per kg'] += cost_kg
                elif price["source"] == 'usp':
                    total_cost_usp['Price according to quantity'] += quantity_price
                    total_cost_usp['Direct price'] += direct_price
                    total_cost_usp['Price per kg'] += cost_kg

                ingredient_prices[ingredient['name']] = True


        print(f'Total cost for ALDI:')
        for key, value in total_cost_aldi.items():
            print(f'{key}: {value}')
        print()
        print(f'Total cost for USP:')
        for key, value in total_cost_usp.items():
            print(f'{key}: {value}')


if __name__ == "__main__":
    price_analysis = PriceAnalysis()
    price_analysis.get_price_for_recipe('950')

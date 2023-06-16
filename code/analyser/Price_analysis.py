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
File containing calculateur price
"""

__authors__ = "Anthony Gugler, Florian Hofmann, Jérémy Jordan"
__date__ = "26.05.2023"
import json
import fractions
import re

class RecipeCostCalculator:
    def __init__(self, recipe_file, ingredient_file):
        self.recipe_file = recipe_file
        self.ingredient_file = ingredient_file

    def get_recipe(self, index):
        with open(self.recipe_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            recipe = data[index]
            print(recipe['name'])
            return recipe

    def parse_quantity(self, quantity_str):
        quantity_str = quantity_str.replace('l', '').strip()  
        # Remove non-numeric parts of the string
        quantity_str = re.sub("[^\d\/\.]", "", quantity_str)
        
        if ',' in quantity_str:  # decimal quantities
            quantity = float(quantity_str.replace(',', '.'))
        elif '%' in quantity_str:  # percentage quantities
            quantity = float(quantity_str.replace('%', ''))*0.01
        elif 'cl' in quantity_str:  # centiliter quantities
            quantity = float(quantity_str.replace('cl', ''))*0.01
        elif 'g' in quantity_str:  # gram quantities
            quantity = float(quantity_str.replace('g', ''))*0.001
        elif 'kg' in quantity_str:  # kilogram quantities
            quantity = float(quantity_str.replace('kg', ''))
        elif 'ml' in quantity_str:  # milliliter quantities
            quantity = float(quantity_str.replace('ml', ''))*0.001
        elif 'l' in quantity_str:  # liter quantities
            quantity = float(quantity_str.replace('l', ''))
        elif 'tasse' in quantity_str:  # cup quantities
            quantity_str = quantity_str.replace('tasse', '')
            quantity = float(fractions.Fraction(quantity_str)) * 0.24
        elif '/' in quantity_str:  # fractions
            quantity = float(fractions.Fraction(quantity_str)) 
        else : 
            quantity = 0.1
        return quantity

    def get_ingredient_costs(self, recipe):
        with open(self.ingredient_file, 'r', encoding='utf-8') as f:  # Change 'filename' to 'self.ingredient_file'
            data = json.load(f)
            ingredient_names = [ingredient['name'] for ingredient in recipe['ingredients']] 
            ingredient_names = list(dict.fromkeys(ingredient_names))
            total_costs = {'USP': {'direct_price': 0, 'quantity_price': 0, 'kg_price': 0}, 
                        'ALDI': {'direct_price': 0, 'quantity_price': 0, 'kg_price': 0}}
            for ingredient_name in ingredient_names:
                quantity = next(ingredient['quantity'] for ingredient in recipe['ingredients'] if ingredient['name'] == ingredient_name) 
                quantity = self.parse_quantity(quantity)
                for source in ['USP', 'ALDI']:
                    for item in data:
                        if item['ingredient'] == ingredient_name and item['source'] == source or ingredient_name in item.get('other_ingredients', []) and item['source'] == source:
                            item['price_per_kg'] = item['price_kg']
                            item['direct_price'] = item['price']
                            if item['price_kg'] != -1: 
                                if quantity == 0:  # Set a default quantity if none 
                                    quantity = 0.1
                                item['quantity_price'] = quantity * item['price_kg']
                            else:
                                item['quantity_price'] = item['price']

                            print(f"Source : {item['source']}")
                            print(f"Ingredient original : {ingredient_name}")
                            print(f"Ingrédient : {item['ingredient']}")
                            print(f"Prix par kg : {item['price_per_kg']}")
                            print(f"Prix direct : {item['direct_price']}")
                            print(f"Prix selon quantité : {item.get('quantity_price', 'Non disponible')}")
                            print("-----------------------------")
                            
                            # add prices 
                            total_costs[source]['kg_price'] += item['price_per_kg']
                            total_costs[source]['direct_price'] += item['direct_price']
                            total_costs[source]['quantity_price'] += item.get('quantity_price', 0)
                            break


        for source in total_costs.keys():
            print(f"\nTotal cost for {source} ingredients:")
            print(f"Price per kg: {round(total_costs[source]['kg_price'],2)}")
            print(f"Direct price: {round(total_costs[source]['direct_price'],2)}")
            print(f"Price according to quantity: {round(total_costs[source]['quantity_price'],2)}")
            

            print("-----------------------------")


def main(recipe_index):
    recipe_file = '../../data/recipe_marmiton.json'
    ingredient_file = '../../data/items_ingredient.json'

    calculator = RecipeCostCalculator(recipe_file, ingredient_file)
    recipe = calculator.get_recipe(recipe_index)
    calculator.get_ingredient_costs(recipe)

if __name__ == "__main__":
    main(4199)  # L'index de la recette à récupérer

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
File containing a class to prorcess the data scraped before analysing it
"""

__authors__ = "Anthony Gugler, Florian Hofmann, Jérémy Jordan"
__date__ = "05.05.2023"

OUTPUT_FILENAME_ALDI = "aldi_processed.json"
OUTPUT_FILENAME_USP = "usp_processed.json"
OUTPUT_FILENAME_MARMITON = "marmiton_distinct_ingredient.json"
OUTPUT_FILENAME_ITEMS = "items_ingredient.json"

import json
import os

class DataProcesser:
    OUTPUT_PATH: str = "./data/"
    SOURCE_MARMITON: str = "Marmiton"
    SOURCE_USP: str = "USP"
    SOURCE_ALDI: str = "ALDI"

    def __init__(self):
        """
        Constructor
        """
        pass


    def __convert_price_per_unit_to_kg(self, price_per_unit):
        """
        convert price per unit to kg.
        @param price_per_unit:
        @return: price per unit in int
        """
        # Remove brackets and separate price and unit
        price, *unit = price_per_unit.strip("()").split("/")
        unit = "/".join(unit)

        # Convert price to float
        try:
            price = float(price)
        except ValueError:
            return None  # not convertible to float

        if "kg" in unit:
            # The price is already in kg
            pass
        elif " g" in unit:
            # Convert the price of 100g or 1g to kg
            price *= 1000 / int(unit.strip(" g"))
        elif "L" in unit:
            # Convert the price of 1L to kg
            price *= int(unit.strip(" L"))
        elif "ml" in unit:
            # Convert the price of 100ml or 1ml to kg
            price *= 10 if '100' in unit else 1000  
            # For unit prices
            price = -1

        return price

    def parse_aldi(self, path_to_json: str) -> None:
        """
        This method process the data scraped from aldi
        :param path_to_json: path to the json file with data scraped from aldi
        POST : json file with ingredient in a standard format
        """
        with open(path_to_json, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        new_data = []
        seen = set()

        for item in data:
            price_kg = self.__convert_price_per_unit_to_kg(item.get("price_per_unit"))
            # Do not include item if price_kg is None
            if price_kg is not None:
                price_kg = round(price_kg, 2)
                new_item = {
                    "source": self.SOURCE_ALDI,
                    "name": item.get("name"),
                    "price_kg": price_kg,
                    "price": float(item.get("price")),
                    "ingredient": "",
                    "link": item.get("url"),
                }
                item_tuple = tuple(new_item.items())
                if item_tuple not in seen:
                    seen.add(item_tuple)
                    new_data.append(new_item)

        with open(self.OUTPUT_PATH + OUTPUT_FILENAME_ALDI, 'w', encoding='utf-8') as file:
            json.dump(new_data, file, ensure_ascii=False, indent=4)
        
        print(f"Nombre d'éléments dans le fichier d'entrée : {len(data)}")
        print(f"Nombre d'éléments dans le fichier de sortie (sans doublons): {len(new_data)}")


    def parse_usp(self, path_to_json: str) -> None:
        """
        This method process the data scraped from the "USP"
        :param path_to_json: path to the json file with data scraped from "USP"
        POST : json file with ingredient in a standard format
        """
        # load the json file to dict
        f = open(path_to_json, encoding='utf-8')
        usp = json.load(f)
        output: [] = []
        for i in usp:
            # --- Delete useless data ---
            # check for price null
            if i["price"] is None:
                continue
            if "/" in i["quantity"]:
                continue
            # create the ingredient with the standard format
            ingredient: {} = {"source": self.SOURCE_USP, "name": i["name"], "price": -1, "ingredient": ""}
            # strip the quantity and the price
            i['quantity'] = i['quantity'].strip()
            i['price'] = i['price'].strip()
            # compute price
            price: float = 0.0
            tmp = str(i["price"]).split(" ")
            # check if price has no space
            if len(tmp) == 1:
                try:
                    price = float(tmp[0])
                except Exception:
                    # split on -
                    tmp2 = tmp[0].split("-")
                    price = (float(tmp2[0]) + float(tmp2[1])) / 2
            elif len(tmp) == 3:
                price = (float(tmp[0]) + float(tmp[2])) / 2.0
            # compute price per kg
            if i['quantity'] == "kg":
                ingredient['price_kg'] = price
            elif i['quantity'] == "g":
                ingredient['price_kg'] = price * 1000
            elif i['quantity'] == "Litre" or i['quantity'] == "l":
                ingredient['price_kg'] = price
            elif "g" in i['quantity']:
                # extract the number of g
                tmp = float(i['quantity'].split("g")[0])
                ingredient['price_kg'] = (price/tmp)*1000
            elif "dl" in i['quantity']:
                # extract the number of g
                tmp = float(i['quantity'].split("dl")[0])
                ingredient['price_kg'] = (price/tmp)*10
            elif "l" in i['quantity']:
                # extract the number of g
                tmp = float(i['quantity'].split("l")[0])
                ingredient['price_kg'] = (price/tmp)
            else:
                ingredient['price_kg'] = -1.0

            # append to list
            output.append(ingredient)

        # write to file
        outfile = open(self.OUTPUT_PATH + OUTPUT_FILENAME_USP, "w", encoding='utf8')
        json.dump(output, outfile, ensure_ascii=False)
        outfile.close()

        
    def parse_marmiton(self, path_to_marmiton_json: str) -> None:
        """
        This method process the data scraped from marmiton
        :param path_to_json: path to the json file with data scraped from marmiton
        POST : json file with ingredient in a standard format
        """
        # Load the input JSON file
        with open(path_to_marmiton_json, encoding="utf8") as f:
            data_marmiton = json.load(f)

        # Extract all the ingredients from each line
        ingredients = []
        for line in data_marmiton:
            for ingredient in line["ingredients"]:
                ingredients.append(ingredient)
                
                
        ingredients_name_list = [d["name"] for d in ingredients]

        ingredients_name_list_sorted = sorted(set(ingredients_name_list))

        print("Le nombre d'ingrédient 'différents' est de : "+str(len(ingredients_name_list_sorted)))
            
        # Save the unique ingredients to a new JSON file
        outfile = open(self.OUTPUT_PATH + OUTPUT_FILENAME_MARMITON, "w", encoding='utf8')
        json.dump(ingredients_name_list_sorted, outfile, ensure_ascii=False)
        outfile.close()

        # get the full list of items from aldi and ups into a single list
        with open(self.OUTPUT_PATH+OUTPUT_FILENAME_USP, encoding="utf8") as f:
            data_ups = json.load(f)
        with open(self.OUTPUT_PATH+OUTPUT_FILENAME_ALDI, encoding="utf8") as f:
            data_aldi = json.load(f)

        data_items = data_ups + data_aldi

        
        print("Le nombre d'item aldi est de : "+str(len(data_aldi)))
        print("Le nombre d'item usp est de : "+str(len(data_ups)))

        print("Le nombre d'item total dans la liste est de : "+str(len(data_items)))

        # for each item, check the full name of the item and check if there is a match in ingredient.
        # if there is a match, add the ingredient to the item under it's ingredient field
        # if there is no match, remove the last word and check again.
        count = 0
        for item in data_items:

            # check the progress and display how many item has been processed
            count += 1
            if count % 500 == 0:
                print("Number processed item is : "+str(count))

            item_name = item["name"]
            
            # change uppercase to lowercase
            item_name = item_name.lower()

            # remove any special characters from the name
            item_name = item_name.replace(",", "")
            item_name = item_name.replace(".", "")
            item_name = item_name.replace(";", "")
            item_name = item_name.replace(":", "")
            item_name = item_name.replace("!", "")
            item_name = item_name.replace("?", "")
            item_name = item_name.replace("(", "")
            item_name = item_name.replace(")", "")
            item_name = item_name.replace("[", "")
            item_name = item_name.replace("]", "")
            item_name = item_name.replace("{", "")
            item_name = item_name.replace("}", "")
            item_name = item_name.replace("-", "")
            item_name = item_name.replace("_", "")
            item_name = item_name.replace("=", "")
            item_name = item_name.replace("+", "")
            item_name = item_name.replace("*", "")
            item_name = item_name.replace("/", "")
            item_name = item_name.replace("\\", "")
            item_name = item_name.replace("|", "")
            item_name = item_name.replace("@", "")
            item_name = item_name.replace("#", "")

            # Go through all ingredient and check the item's name match the ingredient name.
            # if it doesn't match, the item's name is shortened by removing the last word and check again.
            # if the item's name doesn't match any ingredient, it go through the list of ingredient again but the ingredient is shorten as well
            for i in range(6):
                for ingredient in ingredients_name_list_sorted:
                    ingredient_name_tocheck = ingredient
                    if i!=0:
                        ingredient_name_tocheck = " ".join(ingredient_name_tocheck.split(" ")[:-i])
                    if ingredient_name_tocheck == "":
                        continue
                    item_name_tocheck = item_name

                    while item_name_tocheck != "":
                        if ingredient_name_tocheck in item_name_tocheck:
                            item["ingredient"] = ingredient
                            break
                        else:
                            item_name_tocheck = " ".join(item_name_tocheck.split(" ")[:-1])
                    if item_name_tocheck != "":
                        break
                if item["ingredient"] != "":
                    break

        # count the number of item in the list where the ingredient field is not empty
        count_item = 0
        for item in data_items:
            if item["ingredient"] == "":
                count_item += 1

        print("Le nombre d'item qui n'est pas affilié à un ingrédent est : "+str(count_item))

        # count the number of ingredient that doesn't have an item to liked with
        count_ingredient = 0
        for ingredient in ingredients_name_list_sorted:
            for item in data_items:
                if ingredient == item["ingredient"]:
                    count_ingredient += 1
                    break

        print("Le nombre d'ingrédient qui n'a pas d'item affilié est : "+str(count_ingredient))

        # Save the list of items affiliated (or not) to an ingredient to a new JSON file
        outfile = open(self.OUTPUT_PATH + OUTPUT_FILENAME_ITEMS, "w", encoding='utf8')
        json.dump(data_items, outfile, ensure_ascii=False)
        outfile.close()



def main():
    # test
    dp = DataProcesser()
    path_to_aldi_json = './code/scraper/aldi.json'
    dp.parse_aldi(path_to_aldi_json)
    path_to_usp_json = './code/scraper/usp_output.json'
    dp.parse_usp(path_to_usp_json)
    path_to_marmiton_json = "./code/scraper/recipe_marmiton.json"
    dp.parse_marmiton(path_to_marmiton_json)

if __name__ == "__main__":
    main()

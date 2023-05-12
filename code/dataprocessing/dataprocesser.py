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

import json
class DataProcesser:
    OUTPUT_PATH: str = "../"
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

        with open(self.OUTPUT_PATH + 'aldi_out.json', 'w', encoding='utf-8') as file:
            json.dump(new_data, file, ensure_ascii=False, indent=4)
        
        print(f"Nombre d'éléments dans le fichier d'entrée : {len(data)}")
        print(f"Nombre d'éléments dans le fichier de sortie (sans doublons): {len(new_data)}")




    def parse_marmiton(self, path_to_json: str) -> None:
        """
        This method process the data scraped from marmiton
        :param path_to_json: path to the json file with data scraped from marmiton
        POST : json file with ingredient in a standard format
        """
        pass

    def parse_usp(self, path_to_json: str) -> None:
        """
        This method process the data scraped from the "USP"
        :param path_to_json: path to the json file with data scraped from "USP"
        POST : json file with ingredient in a standard format
        """


# def main():
#     # test
#     dp = DataProcesser()
#     path_to_aldi_json = './aldi.json'
#     dp.parse_aldi(path_to_aldi_json)

# if __name__ == "__main__":
#     main()

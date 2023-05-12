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
import os


class DataProcesser:
    OUTPUT_PATH: str = "./"
    SOURCE_USP: str = "USP"

    def __init__(self):
        """
        Constructor
        """
        pass

    def parse_aldi(self, path_to_json: str) -> None:
        """
        This method process the data scraped from aldi
        :param path_to_json: path to the json file with data scraped from aldi
        POST : json file with ingredient in a standard format
        """
        pass

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
        # load the json file to dict
        f = open(path_to_json)
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
            ingredient: {} = {"source": self.SOURCE_USP, "name": i["name"], "price": -1, "ingredient": "-"}
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
        outfile = open(self.OUTPUT_PATH + "usp.json", "w", encoding='utf8')
        json.dump(output, outfile, ensure_ascii=False)
        outfile.close()


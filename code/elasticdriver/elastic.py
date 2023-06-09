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

import json
from elasticsearch import Elasticsearch


class ElasticDriver:

    def __init__(self, host: str='localhost', port: int=9200, user: str='user', password: str='password', scheme: str='http'):
        """
        Constructor

        @param host: The host of the ElasticSearch server
        @param port: The port of the ElasticSearch server
        @param user: The user 
        @param password: The password 
        @param scheme: The scheme to use for connecting to the ElasticSearch.
        all param have default value
        """
        self.elastic = Elasticsearch(hosts=[{'host': host, 'port': port, 'scheme': scheme}], http_auth=(user, password))

    def index_data(self, index_name: str, file_path: str):
        """
        Function to index JSON data file into index in ElasticSearch

        @param index_name: Name of the index
        @param file_path: Path to the JSON data file
        """
        # Open and load JSON data file
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Index data into Elasticsearch
        for i, doc in enumerate(data):
            self.elastic.index(index=index_name, id=i, document=doc)
        print("Data indexing completed")


if __name__ == "__main__":
    driver = ElasticDriver()
    driver.index_data('recipe_marmiton', './data/recipe_marmiton.json')
    driver.index_data('items_ingredient', './data/items_ingredient.json')




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
File containing FastAPI routes & start.
"""

__authors__ = "Anthony Gugler, Florian Hofmann, Jérémy Jordan"
__date__ = "05.05.2023"

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from datetime import datetime
from analyser.analyse import DataAnalyser
from elasticdriver.price_analysis import PriceAnalysis
from dataprocessing.dataprocesser import DataProcesser
from elasticdriver.elastic import ElasticDriver
from threading import Thread
import os

api_description = """
Return the price estimation of a recipe scraped from Marmiton website
"""

# Define the FastAPI application with information
app = FastAPI(
    title="Des recettes et des prix - API",
    description=api_description,
    version="0.0.1",
    swagger_ui_parameters={
        "tagsSorter": "alpha",
        "operationsSorter": "method",
    },
    license_info={
        "name": "MIT License",
        "url": "https://choosealicense.com/licenses/mit/",
    },
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# components
analyser: DataAnalyser = DataAnalyser()
processer: DataProcesser = DataProcesser()
db: ElasticDriver = ElasticDriver()
fetcher: PriceAnalysis = PriceAnalysis()


# Redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs", status_code=301)


@app.on_event("startup")
async def startup_event():
    # check if data is already indexed
    if os.path.exists("./.indexed"):
        return
    print("Creating index...")
    # Index the data using the index_data method
    db.index_data('items_ingredient', '../data/items_ingredient.json')
    db.index_data('recipe_marmiton', '../data/recipe_marmiton_with_cluster.json')
    # create .indexed file to avoid reindexing
    open("./.indexed", "w").close()


@app.get("/recipe/{query}")
async def recipe(query: str):
    recipe: dict = fetcher.query_recipe(query)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return recipe


@app.get("/scrape")
async def scrape():
    def run_scraper():
        print("Start scrape!!!")
        result = os.system('cd scraper && scrapy crawl aldi -O ../../data/aldi.json')
        if result == 0:  # command executed successfully
            print("Scraping completed successfully. Starting post-processing...")
            # # Instantiate the DataProcesser object
            data_processor = DataProcesser()

            # Provide the path to the aldi.json file
            path_to_aldi_json = '../data/aldi.json'

            data_processor.clean_aldi_data(path_to_aldi_json)

            # Call the parse_aldi method
            data_processor.parse_aldi('../data/aldi_clean.json')

            data_processor.parse_marmiton('../data/recipe_marmiton.json')

            # Import the ElasticDriver class
            from elasticdriver.elastic import ElasticDriver

            # Instantiate the ElasticDriver object
            driver = ElasticDriver()

            # Index the data using the index_data method
            driver.index_data('items_ingredient', '../data/items_ingredient.json')

            with open("last_action_timestamp.txt", "w") as f:
                f.write(str(int(datetime.now().timestamp())))
        else:  # command execution failed
            print("Scraping failed. Post-processing is not started.")

    thread = Thread(target=run_scraper)
    thread.start()
    return {"status": "Scraping started"}


@app.get("/price}")
async def recipe(query: str):
    recipe: dict = fetcher.query_recipe(query)
    if recipe is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return recipe


@app.get("/date")
async def last_action_date():
    # read value from last_action_date.txt
    timestamp: int
    with open("last_action_timestamp.txt", "r") as f:
        timestamp = int(f.read())

    # convert timestamp to date
    dt_object = datetime.fromtimestamp(timestamp)
    # return date
    return {
        "last_action_date": str(dt_object)
    }


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)

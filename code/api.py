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
db: ElasticDriver = ElasticDriver("localhost", 9200, "user", "password")
fetcher: PriceAnalysis = PriceAnalysis()


# Redirect to docs
@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs", status_code=301)


@app.on_event("startup")
async def startup_event():
    # TODO : Code before API up (run scraper, ...)
    print("------ Processing data scraped... ------")
    # processer.parse_usp("scraper/usp_output.json")
    print("------ Data processed ------------------")


@app.get("/recipe/{query}")
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

# WEBM - Projet

Gugler Anthony
Hofmann Florian
Jordan Jérémy



## Getting started

The scraper collects recipes from Marmiton, processing the data to fit our database schema. The recipe database stores this processed data, while the ingredient mapping system correlates recipe ingredients with products in Adli and USP stores.

## Background and objectives
We have chosen to combine the famous recipe website Marmiton with two other sites to recover the price of ingredients: the Aldi shop and the Union Suisse des Paysans website. 

Using this data, it will then be possible to carry out analyses to establish whether Marmiton's estimate of the cost of recipes is correct. The correlation between the estimate and the actual price will then be established. A dynamic website will be developed to present the results of the analyses. 

The three types of price below will be presented and compared.
- The price of the Aldi basket: this price takes into account all the products purchased, for example: purchase of 1 kg of carrots in a packet.
- Price per quantity: this price takes into account the weight of the recipe. This price is the minimum you have to pay to make the recipe.
- Average price: the average price between Aldi and Union des paysans.

In addition, the Aldi prices and the recommended prices will be compared.


## Requirement 

- Python 3.10
- Docker with docker-compose
- (ports 80 / 8000 / 9200 / 9300 free)

## Structure
The project contains several directories:

- code — Contains the main project source code and the API to interact with the web app.
- data — Holds data files, such as the database file and any other resources needed.
- doc — Includes documentation files explaining the project and its use.
- webapp — Contains the source code for the web application interface.

## Installation
Follow the steps below to install the project.

### 1. Clone the repository
Clone the repository to your local machine using the following command:
```bash
git clone https://gitlab.forge.hefr.ch/florian.hofmann/webm-projet.git
```

### 2. Start Elasticsearch and the web application
Run the following command to start Elasticsearch and the web application:
```bash
docker-compose up
```

### 3. Start the API
Go on the code directory and run the following command to install all python requirements and start the API:
```bash
pip install -r requirements.txt
python api.py
```

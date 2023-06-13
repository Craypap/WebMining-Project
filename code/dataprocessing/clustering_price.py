import json
import pandas as pd
from sklearn.cluster import KMeans


PATH_COST = "./data/recipe_costs.json"
PATH_RECIPES = "./data/recipe_marmiton.json"
PATH_RECIPES_OUTPUT = "./data/recipe_marmiton_with_cluster.json"
NBR_CLUSTER = 3


# change the id of the cluster so the number 0 is the lowest price and it goes up from there
def change_cluster_id(df, name_prev_column_cluster:str, name_price_column:str, name_new_column_cluster:str):
    # get the cluster id
    cluster_id = df.groupby(name_prev_column_cluster).mean().sort_values(by=name_price_column).reset_index()[name_prev_column_cluster]
    # make a dictionary to map the old cluster id to the new cluster id
    cluster_id_dict = {}
    for i in range(len(cluster_id)):
        cluster_id_dict[cluster_id[i]] = i
    # change the cluster id
    df[name_new_column_cluster] = df[name_prev_column_cluster].map(cluster_id_dict)
    # delete the previous cluster column
    del df[name_prev_column_cluster]
    return df

# print the range of the cluster and the number of recipes in the cluster
def print_range_clustering(df_ALDI, df_USP):
    print("The range of the cluster and the number of recipes in the cluster:")
    print("ALDI:")
    # build an dictionnary of the details of the recipes so it's like that : kmean: {cluster: {range min : range max}, count: {count of recipes in the cluster}}
    kmeans_ALDI_details = {}
    for cluster in df_ALDI['kmeans_cluster_price'].unique():
        kmeans_ALDI_details[cluster] = {}
        kmeans_ALDI_details[cluster]['range'] = [df_ALDI.groupby('kmeans_cluster_price')['Aldi_price'].min()[cluster], df_ALDI.groupby('kmeans_cluster_price')['Aldi_price'].max()[cluster]]
        kmeans_ALDI_details[cluster]['count'] = df_ALDI.groupby('kmeans_cluster_price')['Aldi_price'].count()[cluster]
    # order each key of the dictionnary croissant
    kmeans_ALDI_details = dict(sorted(kmeans_ALDI_details.items()))
    print(kmeans_ALDI_details)
    # USP
    print("USP:")
    kmens_USP_details = {}
    for cluster in df_USP['kmeans_cluster_price'].unique():
        kmens_USP_details[cluster] = {}
        kmens_USP_details[cluster]['range'] = [df_USP.groupby('kmeans_cluster_price')['USP_price'].min()[cluster], df_USP.groupby('kmeans_cluster_price')['USP_price'].max()[cluster]]
        kmens_USP_details[cluster]['count'] = df_USP.groupby('kmeans_cluster_price')['USP_price'].count()[cluster]
    # order each key of the dictionnary croissant
    kmens_USP_details = dict(sorted(kmens_USP_details.items()))
    print(kmens_USP_details)


def main():
    # read in the data that is a json
    with open(PATH_COST, 'r', encoding='utf8') as f:
        data_cost = json.load(f)

    # go throuth the data and get the value and key and make a list of the prices
    recipe_ALDI_prices = []
    recipe_USP_prices = []
    for recipe_name, details in data_cost.items():
        recipe_ALDI_prices.append([recipe_name, details['ALDI']['quantity_price']])
        recipe_USP_prices.append([recipe_name, details['USP']['quantity_price']])

    # make a dataframe of the prices
    df_ALDI = pd.DataFrame(recipe_ALDI_prices, columns=['recipe_name', 'Aldi_price'])
    df_USP = pd.DataFrame(recipe_USP_prices, columns=['recipe_name', 'USP_price'])

    # set up clustering Kmean for the prices
    kmeans_ALDI = KMeans(n_clusters=NBR_CLUSTER, random_state=0).fit(df_ALDI[['Aldi_price']])
    kmeans_USP = KMeans(n_clusters=NBR_CLUSTER, random_state=0).fit(df_USP[['USP_price']])

    # add the cluster labels to the dataframe
    df_ALDI['kmeans_cluster'] = kmeans_ALDI.labels_
    df_USP['kmeans_cluster'] = kmeans_USP.labels_

    df_ALDI = change_cluster_id(df_ALDI, 'kmeans_cluster', 'Aldi_price', 'kmeans_cluster_price')
    df_USP = change_cluster_id(df_USP, 'kmeans_cluster', 'USP_price', 'kmeans_cluster_price')

    # print the range of the cluster and the number of recipes in the cluster
    print_range_clustering(df_ALDI, df_USP)

    # open the recipes json
    with open(PATH_RECIPES, 'r', encoding='utf8') as f:
        data = json.load(f)

    # If 'data' is a dictionary with one key-value pair, extract the list of recipes
    if isinstance(data, dict):
        key = list(data.keys())[0]
        recipes = data[key]
    else:
        recipes = data

    # Adding the ALDI_cluster and USP_cluster to each recipe
    for recipe in recipes:
        # finding cluster id for each recipe from df_ALDI and df_USP
        aldi_cluster_id = df_ALDI.loc[df_ALDI['recipe_name'] == recipe['name'], 'kmeans_cluster_price'].values[0]
        usp_cluster_id = df_USP.loc[df_USP['recipe_name'] == recipe['name'], 'kmeans_cluster_price'].values[0]

        # adding cluster ids to the recipe
        recipe['ALDI_cluster'] = int(aldi_cluster_id)
        recipe['UPS_cluster'] = int(usp_cluster_id)

    # If 'data' is a dictionary, update the recipes under the original key
    if isinstance(data, dict):
        data[key] = recipes

    # Writing the updated data back to a new JSON file
    with open(PATH_RECIPES_OUTPUT, 'w', encoding='utf8') as file:
        json.dump(data, file, ensure_ascii=False)

if __name__ == "__main__":
    main()
import json

# Load the input JSON file
with open("../scraper/recipe_marmiton.json", encoding="utf8") as f:
    data = json.load(f)

# Extract all the ingredients from each line
ingredients = []
for line in data:
    for ingredient in line["ingredients"]:
        ingredients.append(ingredient)
        #print(ingredient["name"])
        
        
ingredients_name_list = [d["name"] for d in ingredients]

ingredients_name_list_sorted = sorted(set(ingredients_name_list))

print("Le nombre d'ingrédient 'différents' est de : "+str(len(ingredients_name_list_sorted)))
    
# Save the unique ingredients to a new JSON file
with open("all_distinct_ingredients.json", "w", encoding="utf-8") as f:
    json.dump(ingredients_name_list_sorted, f, ensure_ascii=False)

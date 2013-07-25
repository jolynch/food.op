from mwlib import dumpparser
import mwlib.uparser as parser
from mwlib.parser.nodes import *
import json

def parse_tree(file_name):
    dp = dumpparser.DumpParser("data/wiki-data.xml")
    data = []
    for recipe in dp:
        data.append( (recipe.pageid,
                      recipe.title,
                      parser.parseString(recipe.text, recipe.text)) )
    return data

def convert_data(data):
    """ Converts the data to good json format

    Input is a list in the form:
    [ (recipe_id, recipe_title, Article object) ...]

    We return a list of dicts of the form
    [ { 'title' : "Pesto",
        'category': "Sauce recipes",
        'servings': ""
        'related_categories': "Medium Difficulty",
        'time' : 45,
        'difficulty': 3,
        'ingredient_count' : 6,
        'ingredients' : [4 oz basil ...],
        'procedure' : "Preheat ...",
      },
        ...
    ]
    """
    final_data = []
    for r_id, r_title, r_data in data:
        try:
            data_item = {
                'title': r_title.replace("Cookbook:", ""),
                'link': "http://en.wikibooks.org/wiki/%s" % r_title,
                'id': r_id
            }
            category, servings, time, difficulty = get_summary(r_data)
            data_item['category'] = category
            data_item['servings'] = servings
            data_item['related_categories'] = get_categories(r_data)
            data_item['time'] = time
            data_item['difficulty'] = difficulty
            ingredients = get_ingredients(r_data)
            data_item['ingredient_count'] = len(ingredients)
            data_item['ingredients'] = ingredients
            data_item['procedure'] = get_procedure(r_data)

            if len(ingredients) > 1:
                final_data.append(data_item)
        except Exception as e:
            pass
    return final_data


def strip_link(al):
    if isinstance(al, ArticleLink):
        return al.target.replace("Cookbook:","")
    else:
        return al

def strip_text(te):
    if isinstance(te, Text):
        return te.caption
    else:
        return te


def get_categories(article):
    categories = article.find(CategoryLink)
    categories = [cat.target.replace("Category:","") for cat in categories]
    categories = [cat.replace("category:","") for cat in categories]
    return categories

def get_summary(article):
    try:
        summary = article.children[0].children[0].caption
        summary_data = summary.partition("}}")[0].split("|")[1:]
        if len(summary_data) == 4:
            return summary_data
        else:
            raise Exception("Invalid node")
    except:
        return [None] * 4

def get_ingredients(article):
    try:
        ingredients = article.find(ItemList)[0].children
        final_ingredients = []
        for ingredient in ingredients:
            text = ingredient.children[0].children
            text = [strip_link(i) for i in text]
            text = [strip_text(i) for i in text]
            final_ingredients.append("".join(text))
        return final_ingredients
    except Exception as e:
        return []

def get_procedure(article):
    try:
        for section in article.find(Section):
            if "Procedure" in section.children[0].asText():
                return section.asText()
    except:
        pass
    return ""

if __name__ == '__main__':
    data = parse_tree("data/wiki-data.xml")
    result = convert_data(data)

    with open("data/recipe.json", "w") as outfile:
        json.dump(result, outfile)


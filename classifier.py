from sklearn.ensemble import GradientBoostingClassifier
from sklearn.naive_bayes import GaussianNB
from models import User, Vote
import json
import nltk
import numpy as np
import random

data_file = open("data/recipe.json")
dataset = json.load(data_file)

category_map = {}
stemmer = nltk.stem.snowball.EnglishStemmer()

def standardize(text):
    if text is None:
        return text
    return stemmer.stem(text.replace("_", " "))

for d in dataset:
    if d['category'] is not None:
        category_map[standardize(d['category'])] = True
    for cat in d['related_categories']:
        if cat is not None:
            category_map[standardize(cat)] = True

counter = 0
for key in category_map.keys():
    category_map[key] = counter
    counter += 1

def data_to_vector(data_item):
    """ Generates N vectors
    1) Difficulty (1-5)
    2) Ingredient Count
    3) Time (s)
    4) Serving Size
    5 .. N) Category ids
    """
    try:
        difficulty = int(data_item['difficulty'])
    except:
        difficulty = 0

    ingredient_count = int(data_item['ingredient_count'])
    time = float(data_item['parsed_time'])
    serving_size = float(data_item['parsed_servings'])
    data_vector = [0] * (4 + len(category_map))
    data_vector[0] = difficulty
    data_vector[1] = ingredient_count
    data_vector[2] = time
    data_vector[3] = serving_size
    categories = []
    categories.append(data_item['category'])
    for cat in data_item['related_categories']:
        categories.append(cat)
    categories = [c for c in categories if c]
    for cat in categories:
        data_vector[category_map[standardize(cat)]] = 1.0

    return np.array(data_vector)


class Classifier(object):
    def train(self, user):
        raise NotImplementedError("You must implment train")

    def predict(self, user):
        raise NotImplementedError("You must implement predict")

class SimilarClassifier(Classifier):
    """ Classifier that things recipes are good if they are similar

    From a user's rating we compute the following:
    1) Most common category
    2) Average difficulty when present
    3) Average ingredient count
    4) Average time
    5) Average serving size

    Distance is computed relative to that in a 5 vector:
    """

    def __init__(self, distance):
        self.data = {}
        self.distance = distance

    def train(self, user):
        votes = Vote.query.filter_by(user=user).all()
        postive_ids = [v.recipe.wiki_id for v in votes if v.vote == 1]
        negative_ids = [v.recipe.wiki_id for v in votes if v.vote == -1]
        print postive_ids
        print negative_ids

class GradientClassifier():
    def __init__(self):
        self.data = {}

    def has_trained(self, user):
        return user in self.data

    def train(self, user):
        votes = Vote.query.filter_by(user=user).all()
        postive_ids = [v.recipe.wiki_id for v in votes if v.vote == 1]
        negative_ids = [v.recipe.wiki_id for v in votes if v.vote == -1]

        positive_data = [dat for dat in dataset if dat['id'] in postive_ids]
        negative_data = [dat for dat in dataset if dat['id'] in negative_ids]

        num_positive = len(positive_data)
        training_data = positive_data + negative_data
        training_data = np.array([data_to_vector(i) for i in training_data])
        training_labels = np.array([1] * num_positive + [-1] * (len(training_data) - num_positive))
        clf = GradientBoostingClassifier(n_estimators=200,
                                         learning_rate=.2,
                                         max_depth=3)
        clf.fit(training_data, training_labels)
        self.data[user] = clf

    def predict(self, user):
        if user not in self.data:
            raise Exception("You need to train first")
        clf = self.data[user]
        predictions = np.array([clf.predict_proba(data_to_vector(d)) for d in dataset])
        x,y,z = predictions.shape
        return predictions.reshape(x, z)

    def guess(self, user, num_predictions=5):
        if user not in self.data:
            raise Exception("You need to train first")
        predictions = self.predict(user)
        spredictions = [(idx, val[1]) for idx, val in enumerate(predictions)]
        spredictions.sort(key = lambda x: x[1])
        previous_votes = Vote.query.filter_by(user=user).all()
        previous_positive_ids = [v.recipe.wiki_id for v in previous_votes if v.vote == 1]

        final = []
        index = len(spredictions) - 1
        while index > 0 and (0 <= len(final) < num_predictions):
            if dataset[spredictions[index][0]]['id'] not in previous_positive_ids:
                final.append(dataset[spredictions[index][0]])
            index -= 1

        return final







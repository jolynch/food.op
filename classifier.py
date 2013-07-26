from sklearn.ensemble import GradientBoostingClassifier
from web import User, Vote
import json

data_file = open("data/recipe.json")
dataset = json.load(data_file)

class Classifier(object):
    def train(self, user):
        raise NotImplementedError("You must implment train")

    def predict(self, user):
        raise NotImplementedError("You must implement predict")

class SimilarClassifier(Classifier):
    def __init__(self, distance):
        self.data = {}

    def train(self, user):
        votes = Vote.query.filter_by(user=user).all()
        postive_ids = [v.wiki_id for v in votes if v.vote == 1]
        negative_ids = [v.wiki_id for v in votes if v.vote == -1]






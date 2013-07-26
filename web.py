from flask import Flask, render_template, jsonify
import json
import os
import random
from models import db, User, Vote, Recipe
from classifier import GradientClassifier

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
app.classifier = GradientClassifier()
db.init_app(app)

with open("data/recipe.json") as infile:
    dataset = json.load(infile)
    recipe_lookup = {}
    for data in dataset:
        recipe_lookup[data['id']] = data

@app.route('/')
def index():
    data = {}
    try:
        with open('data/recipe.json') as infile:
            data = json.load(infile)
    except Exception as e:
        print e
        pass
    return render_template('index.html', data=data)

@app.route('/users/all')
def view_users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/users/view/<int:user_id>')
def view_user(user_id):
    user = User.query.get_or_404(user_id)
    votes = Vote.query.filter_by(user=user).all()
    recipes = [vote.recipe for vote in votes]
    return render_template('show_user.html', user=user, recipes=recipes, votes=votes)


@app.route('/create/<username>', methods=['POST'])
def create_user(username):
    user = User(username)
    db.session.add(user)
    db.session.commit()
    return jsonify(action="create", user=username, id=user.id)

@app.route('/vote/up/<int:user_id>/<int:recipe_id>', methods=['POST'])
def vote_up(user_id, recipe_id):
    user = User.query.get_or_404(user_id)
    recipe = Recipe.query.get_or_404(recipe_id)
    add_vote(user, recipe, 1)
    return jsonify(action="vote-up", user=user.name, recipe=recipe.wiki_id)

@app.route('/vote/down/<int:user_id>/<int:recipe_id>', methods=['POST'])
def vote_down(user_id, recipe_id):
    user = User.query.get_or_404(user_id)
    recipe = Recipe.query.get_or_404(recipe_id)
    add_vote(user, recipe, -1)
    return jsonify(action="vote-down", user=user.name, recipe=recipe.wiki_id)

@app.route('/vote/remove/<int:user_id>/<int:recipe_id>', methods=['POST'])
def vote_remove(user_id, recipe_id):
    user = User.query.get_or_404(user_id)
    recipe = Recipe.query.get_or_404(recipe_id)
    votes = Vote.query.filter_by(user=user, recipe=recipe)
    for vote in votes:
        db.session.delete(vote)
    db.session.commit()
    return jsonify(action="vote-remove", user=user.name, recipe=recipe.wiki_id)


def add_vote(user, recipe, vote):
    dbvote = Vote(user, recipe, vote)
    oldvotes = Vote.query.filter_by(user=user, recipe=recipe).all()
    if oldvotes:
        for ov in oldvotes:
            db.session.delete(ov)

    db.session.add(dbvote)
    db.session.commit()

@app.route('/initialize/<int:user_id>')
def initialize(user_id):
    user = User.query.get_or_404(user_id)
    recipes = random.sample(Recipe.query.all(), 10)
    return render_template('initialize.html', user=user, recipes=recipes)

@app.route('/recipe/<int:recipe_id>')
def get_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id)
    return render_template('recipe.html', recipe=recipe_lookup[recipe.wiki_id])

@app.route('/recommend/<int:user_id>')
def get_recommendation(user_id):
    user = User.query.get_or_404(user_id)
    if not app.classifier.has_trained(user):
        app.classifier.train(user)
    val = app.classifier.guess(user)
    val = [v['id'] for v in val]
    recipes = []
    for v in val:
        recipe = Recipe.query.filter_by(wiki_id=v).first()
        recipes.append(recipe)

    return render_template("show_results.html", user=user, recipes = recipes)


if __name__ == '__main__':
    app.run()

from flask import Flask, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
import json
import os
import random

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
db = SQLAlchemy(app)

with open("data/recipe.json") as infile:
    dataset = json.load(infile)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    votes = db.relationship('Vote', backref='user', lazy='dynamic')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.name

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vote = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))

    def __init__(self, user, recipe, vote):
        self.user = user
        self.recipe = recipe
        self.vote = vote

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wiki_id = db.Column(db.Integer)
    votes = db.relationship('Vote', backref='recipe', lazy='dynamic')

    def __init__(self, wiki_id):
        self.wiki_id = wiki_id

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

@app.route('/create/<username>', methods=['POST'])
def create_user(username):
    user = User(username)
    db.session.add(user)
    db.session.commit()
    return jsonify(action="create", user=username, id=user.id)

@app.route('/vote/up/<int:user_id>/<int:recipe_id>', methods=['POST'])
def vote_up(user_id, recipe_id):
    user = User.query.get_or_404(user_id)
    recipe = Recipe.query.filter_by(wiki_id=recipe_id).first_or_404()
    add_vote(user, recipe, 1)
    return jsonify(action="vote-up", user=user.name, recipe=recipe.wiki_id)

@app.route('/vote/down/<int:user_id>/<int:recipe_id>', methods=['POST'])
def vote_down(user_id, recipe_id):
    user = User.query.get_or_404(user_id)
    recipe = Recipe.query.filter_by(wiki_id=recipe_id).first_or_404()
    add_vote(user, recipe, -1)
    return jsonify(action="vote-down", user=user.name, recipe=recipe.wiki_id)

def add_vote(user, recipe, vote):
    vote = Vote(user, recipe, vote)
    db.session.add(vote)
    db.session.commit()

@app.route('/initialize/<int:user_id>')
def initialize(user_id):
    user = User.query.get_or_404(user_id)
    recipes = random.sample(Recipe.query.all(), 10)
    return render_template('initialize.html', user=user, recipes=recipes)


if __name__ == '__main__':
    app.run()

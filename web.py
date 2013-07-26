from flask import Flask, render_template, jsonify
from flask.ext.sqlalchemy import SQLAlchemy
import json
import os

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///food.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<User %r>' % self.username

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vote = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
            backref=db.backref('votes', lazy='dynamic'))
    recipe_id = db.Column(db.Integer, db.ForeignKey('recipe.id'))
    recipe = db.relationship('Recipe',
            backref=db.backref('votes', lazy='dynamic'))

    def __init__(self, user, recipe, vote):
        self.user = user
        self.recipe = recipe
        self.vote = vote

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    wiki_id = db.Column(db.Integer)

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

@app.route('/create/<username>')
def create_user(username):
    user = User(username)
    db.session.add(user)
    db.session.commit()
    return jsonify(action="create", user=username, id=user.id)

@app.route('/vote/up/<int:user_id>/<int:recipe_id>')
def vote_up(user_id, recipe_id):
    user = User.query.filter_by(id=user_id).get_or_404()
    recipe = Recipe.query.filter_by(id=recipe_id).get_or_404()
    add_vote(user_id, recipe_id, 1)
    return jsonify(action="vote-up", user=user, recipe=recipe)

@app.route('/vote/down/<int:user_id>/<int:recipe_id>')
def vote_down(user_id, recipe_id):
    user = User.query.filter_by(id=user_id).get_or_404()
    recipe = Recipe.query.filter_by(id=recipe_id).get_or_404()
    add_vote(user_id, recipe_id, -1)
    return jsonify(action="vote-up", user=user, recipe=recipe)

def add_vote(user_id, recipe_id, vote):
    vote = Vote(user_id, recipe_id, vote)
    db.session.add(vote)
    db.session.commit()


if __name__ == '__main__':
    app.run()

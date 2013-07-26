from flask import Flask, render_template
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
    user_id = db.relationship('User',
            backref=db.backref('votes', lazy='dynamic'))
    recipe_id = db.relationship('Recipe',
            backref=db.backref('votes', lazy='dynamic'))

class Recipe(db.Mode):
    id = db.Column(db.Integer, primary_key=True)
    wiki_id = db.Column(db.Integer)

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

if __name__ == '__main__':
    app.run()

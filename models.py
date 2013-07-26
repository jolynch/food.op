from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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



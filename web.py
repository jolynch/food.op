from flask import Flask, render_template
import json
app = Flask(__name__)
app.debug = True

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

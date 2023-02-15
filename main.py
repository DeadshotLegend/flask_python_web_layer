import threading

# import "packages" from flask
from flask import render_template  # import render_template from "public" flask libraries

# import "packages" from "this" project
from __init__ import app  # Definitions initialization

@app.errorhandler(404)  # catch for URL not found
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')  
def index():
    return render_template("index.html")

@app.route('/snakes')  
def snakes():
    return render_template("snakes.html")

@app.route('/snake_game/')
def render_static():
    return render_template('snake_game.html')

@app.route('/snake_game/snake_apk/')
def render_static_snakeapk():
    return render_template('snake.apk')


# this runs the application on the development server
if __name__ == "__main__":
    #app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///snake.db'
    app.run(debug=True, host="0.0.0.0", port="8096")
#    initNFLTeams()

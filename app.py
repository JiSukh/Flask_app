import flask
from config import app



@app.route('/')
def index():
    return flask.render_template("home/index.html")

#too many requests
@app.errorhandler(429)
def too_many_requests(e):
    return flask.render_template('errors/429.html'), 429


if __name__ == '__main__':
    app.run()
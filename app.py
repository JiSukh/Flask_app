import flask
from config import app



@app.route('/')
def index():
    return flask.render_template("home/index.html")


if __name__ == '__main__':
    app.run()
import flask

app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template("home/index.html")

@app.route('/account/')
def account():
    return flask.render_template("accounts/account.html")

@app.route('/login/')
def login():
    return flask.render_template("accounts/login.html")
    
@app.route('/')
def posts():
    return flask.render_template("posts/posts.html")

@app.route('/')
def update():
    return flask.render_template("posts/update.html")

@app.route('/')
def security():
    return flask.render_template("security/security.html")


    


if __name__ == '__main__':
    app.run()
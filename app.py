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

@app.route('/registration/')
def registration():
    return flask.render_template("accounts/registration.html")

@app.route('/create/')
def create():
    return flask.render_template("posts/create.html")
    
@app.route('/posts')
def posts():
    return flask.render_template("posts/posts.html")

@app.route('/update')
def update():
    return flask.render_template("posts/update.html")

@app.route('/security')
def security():
    return flask.render_template("security/security.html")


    


if __name__ == '__main__':
    app.run()
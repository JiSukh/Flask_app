import flask
# IMPORT BLUEPRINTS
from accounts.views import accounts_bp
from posts.views import posts_bp
from security.views import security_bp

app = flask.Flask(__name__)


@app.route('/')
def index():
    return flask.render_template("home/index.html")


## Add blueprints

app.register_blueprint(accounts_bp)
app.register_blueprint(posts_bp)
app.register_blueprint(security_bp)




    


if __name__ == '__main__':
    app.run()
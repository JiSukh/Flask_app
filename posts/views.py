from flask import Blueprint, render_template, flash, url_for, redirect
import config
from posts.forms import PostForm
from sqlalchemy import desc



posts_bp = Blueprint('posts', __name__, template_folder='templates')


@posts_bp.route('/create/', methods=('GET', 'POST'))
def create():
    form = PostForm()

    if form.validate_on_submit():
        new_post = config.Post(title=form.title.data, body=form.body.data)

        config.db.session.add(new_post)
        config.db.session.commit()

        flash('Post created', category='success')
        return redirect(url_for('posts.posts'))

    return render_template('posts/create.html', form=form)
    
@posts_bp.route('/posts')
def posts():
    all_posts = config.Post.query.order_by(desc('id')).all()
    return render_template('posts/posts.html', posts=all_posts)

@posts_bp.route('/update')
def update():
    return render_template("posts/update.html")
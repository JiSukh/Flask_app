from flask import Blueprint, render_template, flash, url_for, redirect
from flask_login import current_user
import config
from posts.forms import PostForm
from sqlalchemy import desc



posts_bp = Blueprint('posts', __name__, template_folder='templates')


@posts_bp.route('/create/', methods=('GET', 'POST'))
def create():
    form = PostForm()



    if form.validate_on_submit():
        new_post = config.Post(userid=current_user.get_id(),title=form.title.data, body=form.body.data)

        config.db.session.add(new_post)
        config.db.session.commit()

        flash('Post created', category='success')
        return redirect(url_for('posts.posts'))

    return render_template('posts/create.html', form=form)
    
@posts_bp.route('/posts')
def posts():
    all_posts = config.Post.query.order_by(desc('id')).all()
    return render_template('posts/posts.html', posts=all_posts)

@posts_bp.route('/<int:id>/update', methods=('GET', 'POST'))
def update(id):

    post_to_update = config.Post.query.filter_by(id=id).first()

    if not post_to_update:
        return redirect(url_for('posts.posts'))

    form = PostForm()

    if form.validate_on_submit():
        post_to_update.update(title=form.title.data, body=form.body.data)

        flash('Post updated', category='success')
        return redirect(url_for('posts.posts'))

    form.title.data = post_to_update.title
    form.body.data = post_to_update.body

    return render_template('posts/update.html', form=form)

@posts_bp.route('/<int:id>/delete')
def delete(id):
    config.Post.query.filter_by(id=id).delete()
    config.db.session.commit()

    flash('Post deleted', category='success')
    return redirect(url_for('posts.posts'))
from flask import Blueprint, render_template, flash, url_for, redirect
from flask_login import current_user,login_required
from posts.forms import PostForm


from utils import roles_required, Sym_Encryption
from models import Post

from sqlalchemy import desc



posts_bp = Blueprint('posts', __name__, template_folder='templates')


@posts_bp.route('/create/', methods=('GET', 'POST'))
@login_required
@roles_required('end_user')
def create():
    form = PostForm()

    if form.validate_on_submit():
        Post.create_post(current_user,form.title.data,form.body.data)

        flash('Post created', category='success')
        return redirect(url_for('posts.posts'))

    return render_template('posts/create.html', form=form)
    
@posts_bp.route('/posts')
@login_required
@roles_required('end_user')
def posts():

    all_posts = Sym_Encryption.decrypt_all_posts(Post.get_all_posts())
    return render_template('posts/posts.html', posts=all_posts)

@posts_bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
@roles_required('end_user')
def update(id):


    if check_current_user_created_post(id):
        post_to_update = Sym_Encryption.decrypt_post(Post.get_post(id))

        if not post_to_update:
            flash('Post not found.', category='warning')
            return redirect(url_for('posts.posts'))

        form = PostForm()

        if form.validate_on_submit():
            new_title = Sym_Encryption.encrypt_text(current_user, form.title.data)
            new_body = Sym_Encryption.encrypt_text(current_user, form.body.data)
            
            post_to_update.update(title=new_title, body=new_body)
            flash('Post updated', category='success')
            return redirect(url_for('posts.posts'))


        form.title.data = post_to_update.title
        form.body.data = post_to_update.body

        return render_template('posts/update.html', form=form)
    else:
        flash('You did not post this post.', category='warning')
        return redirect(url_for('posts.posts'))

@posts_bp.route('/<int:id>/delete')
@login_required
@roles_required('end_user')
def delete(id):




    if check_current_user_created_post(id):
        Post.delete(id)

        flash('Post deleted', category='success')
        return redirect(url_for('posts.posts'))
    else:
        flash('You did not post this post.', category='warning')
        return redirect(url_for('posts.posts'))
    

def check_current_user_created_post(id):
    return current_user.id == Post.query.filter_by(id=id).first().userid

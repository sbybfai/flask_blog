import time
from flask import render_template, request, redirect, url_for, flash, current_app, abort, session, Response
from flask_login import current_user, login_required
from sqlalchemy import or_

from . import main
from .. import db
from ..models import User, Role, Permission, Post, Comment, Category
from .forms import EditProfileForm, EditProfileAdminForm, PostForm, CommentForm
from ..decorators import admin_required, permission_required
from flask_sqlalchemy import get_debug_queries
from collections import defaultdict

@main.after_app_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= current_app.config['FLASKY_SLOW_DB_QUERY_TIME']:
            current_app.logger.warning(
                'Slow query: %s\nParameters: %s\nDuration: %fs\nContext: %s\n'
                % (query.statement, query.parameters, query.duration,
                   query.context))
    return response

@main.route('/shutdown')
def server_shutdown():
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@main.route('/', methods=['GET', 'POST'])
def index():
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(page,
                                                                per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],
                                                                error_out=False)
    posts = pagination.items

    categories = Category.query.all()
    return render_template('index.html', posts=posts, pagination=pagination, categories=categories)


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False)
    posts = pagination.items
    return render_template('user.html', user=user, posts=posts,
                           pagination=pagination)


@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('您的个人信息已更改')
        return redirect(url_for('.user', username=current_user.username))
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.update_email(form.email.data)
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.about_me = form.about_me.data
        db.session.add(user)
        db.session.commit()
        flash("信息已更改")
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


@main.route('/post/<int:id>', methods=['GET'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    page = request.args.get('page', 1, type=int)

    if page == -1:
        page = (post.comments.count() - 1) // \
               current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('post.html', post=post, postForm=form,
                           comments=comments, pagination=pagination)

@main.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():
    if not current_user.can(Permission.WRITE):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, category_id=form.category.data, summary=form.summary.data,
                    body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.index'))
    return render_template('create_post.html', form=form)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.category_id = form.category.data
        post.summary = form.summary.data
        post.body = form.body.data
        db.session.add(post)
        db.session.commit()
        flash('文章已更新')
        return redirect(url_for('.post', id=post.id))

    form.title.data = post.title
    form.category.default = post.category_id
    form.summary.data = post.summary
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/delete/<int:id>')
@login_required
def delete_post(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('删除成功')
    return redirect(url_for('.index'))



@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/category/<int:id>')
def category(id):
    category = Category.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = category.posts.order_by(Post.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],
        error_out=False
    )
    posts = pagination.items
    return render_template('category.html', category=category, posts=posts, pagination=pagination)

@main.route('/archive')
def archive():
    years = defaultdict(dict)
    posts = Post.query.all()
    for post in posts:
        create_time = post.timestamp
        year = create_time.year
        month = create_time.month
        day = create_time.day
        date = "%s-%s" % (month, day)

        months = years[year]
        dateDict = months.setdefault(month, {})
        postList = dateDict.setdefault(date, [])
        postList.append(post)
    return render_template('archive.html', years=years)


@main.route('/comment/<int:id>', methods=['POST'])
def add_comment(id):
    if not current_user.can(Permission.COMMENT):
        abort(403)
    now_time = time.time()
    last_time = session.get("last_comment_time")
    if last_time and now_time - last_time < 60:
        abort(Response('发言太频繁'))

    session['last_comment_time'] = now_time
    post = Post.query.get_or_404(id)
    form = CommentForm()
    replay_id = form.replay_id.data
    if replay_id:
        Comment.query.get_or_404(replay_id)

    comment = Comment(body=form.body.data,
                      post=post,
                      user_name=form.name.data,
                      email=form.email.data,
                      url=form.url.data,
                      replay_id = replay_id,
                      )
    db.session.add(comment)
    db.session.commit()
    flash('您的评论已发布')
    return redirect(url_for('.post', id=post.id, page=-1))

@main.route('/search/')
def search():
    key_word = request.args.get('keyWord', "")
    key_word = "%" + key_word + "%"
    page = request.args.get("page", 1, type=int)
    pagination = Post.query.filter(or_(Post.title.like(key_word), Post.summary.like(key_word)))\
        .order_by(Post.timestamp.desc())\
        .paginate(page,per_page=current_app.config["FLASKY_POSTS_PER_PAGE"],error_out=False)
    posts = pagination.items
    categories = Category.query.all()
    return render_template('index.html', posts=posts, pagination=pagination, categories=categories)


@main.route('/about')
def about():
    return render_template('about.html')
from flask import render_template, flash, redirect, url_for, request
from app import app, db, Config
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, ResetPasswordRequestForm, ResetPasswordForm, RegisterMessageForm
from app.email import send_password_reset_email, register_hello_message
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from werkzeug.urls import url_parse
from datetime import datetime
import random


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        """Забираем данные из формы добавления нового сообщения."""
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Опубликовано новое сообщение')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    """
    Определяем номер страницы для отображения: либо из аргумента page запроса страницы (request.args.get), 
    либо по умолчанию это 1.
    page = номер страницы.
    app.config(['POSTS_PER_PAGE'] - количество элементов на странице.
    True/False - флаг ошибки. Если True, когда запрашивается страница вне диапазона, 404 ошибка будет автоматически возвращена клиенту. 
    Если False, пустой список будет возвращен для страниц вне диапазона.
    """
    posts = current_user.followed_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    """Проверяем, существует ли следующая страница, в противном случае возвращаем None"""
    next_url = url_for(
        'index', page=posts.next_num) if posts.has_next else None
    """Проверяем, существует ли предыдущая страница, в противном случае возвращаем None"""
    prev_url = url_for(
        'index', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Home', form=form,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Неправильный логин или пароль\nПопробуйте еще раз')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Маршрут регистрации нового пользователя
    Проверяем, что пользователь не вошел в систему, в противном случае ->\
        перенаправляем на индексную страницу
    Если пользователь ввел данные в форму, данные провалидированы и действительны ->\
        забираем данные из формы, создаем нового пользователя, отправляем привественное сообщение на email
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            register_hello_message(user, password=form.password.data)
        flash('Вы успешно зарегистрировались.')
        flash('Проверьте ваш почтовый ящик.')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    """Получаем самые новые сообщения, делаем разбивку на страницы"""
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    """Проверяем, существует ли следующая страница, в противном случае возвращаем None"""
    next_url = url_for('user', username=user.username,
                       page=posts.next_num) if posts.has_next else None
    """Проверяем, существует ли предыдущая страница, в противном случае возвращаем None"""
    prev_url = url_for('user', username=user.username,
                       page=posts.prev_num) if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('You changes have been saved')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/follow/<username>')
@login_required
def follow(username):
    """Маршрут создания подписки на пользователя."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} is not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('index'))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    """Маршрут отписки от пользователя."""
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} is not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('index'))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are unfollow {}'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/explore')
@login_required
def explore():
    """Эта страница будет работать как главная страница, но она будет
    показывать глобальный поток сообщений от всех пользователей."""
    page = request.args.get('page', 1, type=int)
    """Получаем самые новые сообщения, делаем разбивку на страницы"""
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False
    )
    """Проверяем, существует ли следующая страница, в противном случае возвращаем None"""
    next_url = url_for(
        'explore', page=posts.next_num) if posts.has_next else None
    """Проверяем, существует ли предыдущая страница, в противном случае возвращаем None"""
    prev_url = url_for(
        'explore', page=posts.prev_num) if posts.has_prev else None

    return render_template('index.html', title='Home',
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    """Маршрут страницы для ЗАПРОСА сброса пароля."""
    if current_user.is_authenticated:
        """Проверка что пользователь не вошел в систему."""
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        """Форма отправлена и действительна."""
        """Запрос в базу данных на существование зарегистрированного электронного адреса в системе"""
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('Письмо с дальнейшими инструкциями было отправлено на ваш почтовый ящик')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html', title='Восстановление доступа', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Первым шагом удостоверяемся, что пользователь не вошел в систему Далее
    определяем, кто пользователь, вызывая метод проверки токена в классе User\
    этот метод возвращает пользователя, если токен действителен, или None, если
    нет.

    Если токен действителен, то представляем пользователю вторую форму,
    в которой запрашивается новый пароль.
    """
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Ваш пароль успешно изменен')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)

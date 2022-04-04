from email.policy import default
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
from hashlib import md5

"""Добавление вспомогательной таблицы подписчиков/подписок в базу данных"""
followers = db.Table(
    'followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(
            digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """Формируем запрос на проверку отношения, существует ли связь между
        двумя пользователями."""
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        """Функция поиска последних сообщений пользователей, на которых
        подписан данный (followed) пользователь.

        :Общая структура запроса: Post.query.join(...).filter(...).order_by(...)
        :join: вызываем операцию join в таблице posts, этим вызовом формируем запрос, чтобы база данных создавала временную таблицу, которая объединяет данные из таблиц posts и followers. Условие в том, что поле followed_id таблицы followers должно быть равно user_id таблицы posts.
        :filter: после того, как операция join дала мне список всех сообщений, за которыми следит какой-то пользователь, я обрезаю этот список методом filter(), чтобы получить результат выполнения для одного отдельно взятого пользователя (по идентифатору пользователя self.id) --> другими словами, сохраняем только те записи, в которых наш пользователь является подписчиком
        """
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        """Получаем свои собственные сообщения."""
        own = Post.query.filter_by(user_id=self.id)
        """Объединяем два списка и отсортировываем результаты в порядке убывания. При таком условии первым результатом будет самый последний пост в блоге."""
        return followed.union(own).order_by(Post.timestamp.desc())


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))

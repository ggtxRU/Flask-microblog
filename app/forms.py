from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo, Length
from app import email
from app.models import User


class LoginForm(FlaskForm):
    """Форма входа в систему."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    """Форма регистрации клиента."""
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[
                              DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        """Проверяем, что имя пользователя, введенное в форму, не существует в
        базе данных."""
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Это имя пользователя уже занято')

    def validate_email(self, email):
        """Проверяем, что почтовый ящик, введенный в форму, не существует в
        базе данных."""
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Этот почтовый ящик уже используется')


class EditProfileForm(FlaskForm):
    """Форма изменения данных на странице."""
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        """Получаем изначальный username пользователя, до попытки изменить его,
        в переменную original_username."""
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        """Сравниваем, чтобы измененный и оригинальный username не совпадали,
        далее проверяем чтобы этот username не был занят другим
        пользователем."""
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('Please use a different username!')


class PostForm(FlaskForm):
    """Форма, в которой пользователи могут добавлять новые сообщения на своих
    страницах."""
    post = TextAreaField('Что нового?', validators=[
                         DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Отправить')


class ResetPasswordRequestForm(FlaskForm):
    """Форма запроса сброса пароля"""
    email = StringField('Email указанный при регистрации аккаунта', validators=[DataRequired(), Email()])
    submit = SubmitField('Восстановить доступ')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('Новый пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Изменить пароль')


class RegisterMessageForm(FlaskForm):
    """Форма отправки смс подтвержждения на электронную почту при регистрации"""
    key = StringField('Введите код подтверждения', validators=[
                                                        DataRequired(), Length(min=1, max=4)])
    submit = SubmitField('Подтвердить')
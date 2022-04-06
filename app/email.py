from flask_mail import Message
from app import mail, app
from flask import render_template
from threading import Thread


def send_async_email(app,msg):
    with app.app_context():
        mail.send(msg)

def send_mail(subject, sender, recipients, html_body):
    """Фунция, отправляющая письмо на email
    :subject: тема письма
    :sender: отправитель
    :recipients: получатель
    :msg.body: содержание письма
    :msg.html: разметка в письме
    """
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.html = html_body
    Thread(target=send_async_email, args=(app,msg)).start()


def send_password_reset_email(user):
    """Фунция генерации токена и отправки сообщения на email"""
    token = user.get_reset_password_token()
    send_mail('[Microblog] Reset Your Password', 
            sender=app.config['ADMINS'][0],
            recipients=[user.email],
            html_body=render_template('email/reset_password.html', user=user, token=token))
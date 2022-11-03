from . import payment_blueprint
from flask import render_template, request, redirect, url_for, current_app
from ..tasks import send_celery_email

@payment_blueprint.route('/')
def index():
    current_app.logger.info("Donate page loading")
    return render_template('payment/donate.html')

@payment_blueprint.route('/payment_success/<string:email>')
def donate(email):
    message_data = {
        'subject': 'Hello from flask app',
        'body': 'Email test using Celery',
        'recipients': email,
    }
    send_celery_email.apply_async(args=[message_data])
    return render_template('payment/thankyou.html', email=email)
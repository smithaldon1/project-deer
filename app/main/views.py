from . import main_blueprint
from flask import render_template, request, redirect, url_for, current_app, abort
from app import db

@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        current_app.logger.info("POST to index()")
        email = request.form.get(u'email')
        try:
            update_firebase(email)
        except Exception as e:
            print(e)
        title = "Subscribed"
        htag = "Thank you for subscribing!"
        ptag = f"Thank you for subscribing to the Greenville United Football club newsletter. We hope you will consider donating to our organization to help better all of Eastern NC. You will receive our newsletter to the following email:  {email}"
        return render_template('thank-you.html', title=title, htag=htag, ptag=ptag)
    
    if request.method == 'GET':
        return render_template('main/index.html', d_amount='1000', goal='50,000', title='Home')

@main_blueprint.route('/terms-and-conditions')
def show_toc(): 
    return render_template('main/terms.html', title="Terms and Conditions")

@main_blueprint.route('/privacy-policy')
def show_pp():
    return render_template('privacy-policy.html', title="Privacy Policy")


### Helper Functions ###
def update_firebase(email):
    f_data = {u'email': email, u'has_donated': 'false', u'is_subscribed': 'true'}
    doc_ref = db.collection(u'newsletter_dl').document(email)
    doc_ref.set(f_data)
    return doc_ref.get(email)

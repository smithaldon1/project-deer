from . import main_blueprint
from flask import render_template, request, redirect, url_for, current_app, abort

@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        current_app.logger.info("POST to index()")
        return render_template(template_name_or_list)
    
    if request.method == 'GET':
        return render_template('main/index.html', d_amount='1000', goal='50,000',)


@main_blueprint.route('/terms-and-conditions')
def show_toc(): 
    return render_template('main/terms.html')

@main_blueprint.route('/privacy-policy')
def show_pp():
    return render_template('privacy-policy.html')
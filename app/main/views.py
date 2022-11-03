from . import main_blueprint
from flask import render_template, request, redirect, url_for, current_app, abort

@main_blueprint.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        current_app.logger.info("POST to index()")
    
    if request.method == 'GET':
        return render_template('main/index.html')

@main_blueprint.route('/admin')
def admin():
    abort(400)
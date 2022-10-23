import bottle
from bottle import (
    route, 
    run, 
    jinja2_template as template, 
    jinja2_view as view, 
    static_file,
)


@route('/')
@view('index.html')
def index():
    return { 'Hello There': 'General Kenobi' }

@route('/donate')
@view('donate.html')
def load_donate_page(amount=None):
    return 

# Serve stylesheets
@route('/css/<filename>')
def stylesheets(filename):
    return static_file(filename, root='./static/css/')

# Serve images
@route('/img/<filename>')
def stylesheets(filename):
    return static_file(filename, root='./static/img/')

# Serve javascript
@route('/js/<filename>')
def stylesheets(filename):
    return static_file(filename, root='./static/js/')

run(host='127.0.0.1', debug=True, reloader=True, port=8080)
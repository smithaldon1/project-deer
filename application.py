from app import create_app

application = create_app()

if __name__ == '__main__':
    application.run(host='0.0.0.0', ssl_context='adhoc', port=8000)
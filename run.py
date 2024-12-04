# run.py

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(ssl_context=('./key/cert.pem', './key/key.pem'))

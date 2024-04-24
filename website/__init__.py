from flask import Flask
import sys, os

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'Chess'

    #make shots directory to save pics
    try:
        os.mkdir('./shots')
    except OSError as error:
        pass

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app
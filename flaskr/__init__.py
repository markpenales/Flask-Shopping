from flask import Flask, render_template, g, url_for
import os

from flaskr.db import init_app
from . import auth
from . import shop

UPLOAD_FOLDER = 'images/items'

def create_app(test_config=None):

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='32137a35e6acd02701d79843720a360029e77fc19a78fc378b848331d0de8aea',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    @app.route('/')
    def index():
        if g.user is None or g.user['type'] == 'user':
            return render_template('index.html')
            
        elif g.user['type'] == 'admin':
            return render_template(('shop/admin/index.html'))
    
    init_app(app)
    app.register_blueprint(auth.bp)
    app.register_blueprint(shop.bp)
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    return app
import os

from flask import Flask, render_template, request

IMAGES_FOLDER = os.path.join('static', 'images')

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        UPLOAD_FOLDER = IMAGES_FOLDER,
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/')
    def hello():
        full_filename = os.path.join(app.config['UPLOAD_FOLDER'], 'bigmap.png')
        return render_template('hello.html', map_image = full_filename)

    return app
    
    
if __name__ == '__main__':
    app = create_app()
    app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', 8080)))
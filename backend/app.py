from flask import Flask
from flask_cors import CORS
from config import Config
from flask_migrate import Migrate

from routes.api.authentification.authentification import auth_bp
from routes.api.rankings.rankings import rankings_bp
from models import db
from utils.logging_config import setup_logging



def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize CORS
    CORS(app,
         origins=['http://localhost:3000'], # React App Url
         allow_headers=['Content-type', 'Authorization'], # Allow JWT headers
         methods=['GET', 'POST', 'PUT', 'DELETE'], # Allowed HTTP methods
         supports_credentials=True) # Allow cookies later if needed

    # Initializes database with app
    db.init_app(app)

    # Migrations initialized
    migrate = Migrate(app, db)

    # BLUEPRINTS
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(rankings_bp, url_prefix='/api/rankings')

    # The whole app will run on the homepage and make API requests to the backend
    # to get information.
    @app.route('/')
    def hello():
        return "Hello World! Flask is running"
    
    # Create database tables
    with app.app_context():
        db.create_all()

    # Initialize logging FIRST
    setup_logging(app)
    
    # Then start scheduler
    with app.app_context():
        from tasks.scheduler import start_scheduler
        start_scheduler()
    
    return app


if __name__ == '__main__':
    app = create_app()
    # Actually makes the server run.
    app.run(host='0.0.0.0', port=5002, debug=True)
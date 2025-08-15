import os
from flask import Flask, send_file
from flask_cors import CORS
from config import Config
from flask_migrate import Migrate

from routes.api.authentification.authentification import auth_bp
from routes.api.rankings.rankings import rankings_bp
from models import db, Player
from utils.logging_config import setup_logging
from tasks.scheduler import start_scheduler, trigger_manual_update



def create_app():
    app = Flask(__name__, static_folder='build', static_url_path='')
    app.config.from_object(Config)
    
    return app


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app = create_app()

    # Moved db and other initialization so that Railway
    # can serve app immediately.
    # CORS configuration based on environment
    if app.config.get('DEBUG'):
        # Development: Allow React dev server
        cors_origins = ['http://localhost:3000', 'http://localhost:3001']
    else:
        # Production: Same origin only (Flask serves React)
        cors_origins = []

    # Initialize CORS
    CORS(app,
         origins=cors_origins, # React App Url
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

    # SERVE REACT
    def serve_react_app():
        """Serve the React app's index.html file"""
        try:
            return send_file(os.path.join(app.static_folder, 'index.html'))
        except FileNotFoundError:
            return """
            <h1>React App Not Built</h1>
            <p>Run <code>npm run build</code> in your frontend directory first.</p>
            """, 404
        
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        """Catch-all route for React SPA"""
        # Don't serve React app for API routes
        if path.startswith('api/'):
            return {'error': 'API endpoint not found'}, 404
        
        # Serve React app for all other routes
        return serve_react_app()
    
    @app.errorhandler(404)
    def not_found(error):
        """Custom 404 handler"""
        from flask import request
        if request.path.startswith('/api/'):
            return {'error': 'API endpoint not found'}, 404
        else:
            return serve_react_app()
    
    # Create database tables
    with app.app_context():
        db.create_all()

    # Initialize logging FIRST
    setup_logging(app)
    
    # Then start scheduler
    with app.app_context():
        start_scheduler()

    # Check if database needs initial population
    with app.app_context():
        
        # If no players exist, populate database
        if Player.query.count() == 0:
            print("Database is empty - triggering initial population...")
            trigger_manual_update()

    # Actually makes the server run.
    # PRODUCTION: app.run(host='0.0.0.0', port=5002, debug=True)
    app.run(host='0.0.0.0', port=port, debug=False)

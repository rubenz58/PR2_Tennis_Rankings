# Minimal test version of app.py
import os
from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)
    
    @app.route('/')
    def home():
        return jsonify({
            'status': 'success',
            'message': 'Tennis Rankings App is running!',
            'port': os.environ.get('PORT', 'not set'),
            'host': '0.0.0.0'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'health': 'ok'})
    
    return app

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Creating minimal Flask app on port {port}...")
    app = create_app()
    print("Minimal Flask app created successfully")
    
    print(f"Starting server on 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)

""" import os
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
    
    # CORS configuration
    if app.config.get('DEBUG'):
        cors_origins = ['http://localhost:3000', 'http://localhost:3001']
    else:
        cors_origins = []
    
    CORS(app,
        origins=cors_origins,
        allow_headers=['Content-type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE'],
        supports_credentials=True)
    
    # Database initialization
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(rankings_bp, url_prefix='/api/rankings')
    
    # React serving routes
    def serve_react_app():
        try:
            return send_file(os.path.join(app.static_folder, 'index.html'))
        except FileNotFoundError:
            return "<h1>React App Not Built</h1>", 404
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        if path.startswith('api/'):
            return {'error': 'API endpoint not found'}, 404
        return serve_react_app()
    
    @app.errorhandler(404)
    def not_found(error):
        from flask import request
        if request.path.startswith('/api/'):
            return {'error': 'API endpoint not found'}, 404
        else:
            return serve_react_app()
    
    return app


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    print("Creating Flask app...")
    app = create_app()
    print("Flask app created successfully")
    
    # Heavy Operations outside of app creation:
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("Database tables created")
        
        print("Setting up logging...")
        setup_logging(app)
        print("Logging setup complete")
        
        print("Starting scheduler...")
        start_scheduler()
        print("Scheduler started")
    
    print(f"Starting Flask server on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=False)
    # PRODUCTION: app.run(host='0.0.0.0', port=5002, debug=True) """

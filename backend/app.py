import os
from flask import Flask, send_file
from flask_cors import CORS
from config import Config
from flask_migrate import Migrate

from routes.api.authentification.authentification import auth_bp
from routes.api.rankings.rankings import rankings_bp
from routes.admin.admin import admin_bp
from models import db, Player
from utils.logging_config import setup_logging
from tasks.scheduler import start_scheduler, trigger_manual_update



def create_app():
    print("\n########## CREATING APP ##########")
    app = Flask(__name__, static_folder='build', static_url_path='')
    app.config.from_object(Config)

    # Environment-based CORS configuration
    is_development = (
        app.config.get('DEBUG') or 
        os.environ.get('FLASK_ENV') == 'development'
    )

    if is_development:
        # Development: Enhanced request logging
        @app.before_request
        def log_request_info():
            from flask import request
            print(f"🔍 {request.method} {request.url}")
            
            # Only check JSON for requests that should have JSON
            if request.method in ['POST', 'PUT', 'PATCH'] and request.is_json:
                print(f"📝 Request Body: {request.json}")

    if is_development:
        # Development: Allow React dev server
        cors_origins = ['http://localhost:3000', 'http://localhost:3001']
        print("Running in DEVELOPMENT mode")
    else:
        # Production: Same origin only (Flask serves React)
        cors_origins = []
        print("Running in PRODUCTION mode")

    print(f"cors_origins: {cors_origins}")

    CORS(app,
        origins=cors_origins,
        allow_headers=['Content-type', 'Authorization'],
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        supports_credentials=True)
    
    # Database initialization
    db.init_app(app)
    migrate = Migrate(app, db)
    
    # Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(rankings_bp, url_prefix='/api/rankings')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    
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

def initialize_app_services(app, is_development):
    """Initialize heavy services based on environment"""
    with app.app_context():
        print("Creating database tables...")
        db.create_all()
        print("✅ Database tables created")
        
        print("Setting up logging...")
        setup_logging(app)
        print("✅ Logging setup complete")
        
        if not is_development:
            # Only start scheduler in production
            print("Starting scheduler...")
            start_scheduler()
            print("✅ Scheduler started")
        else:
            print("⚠️ Scheduler disabled in development mode")


if __name__ == '__main__':
    is_development = os.environ.get('FLASK_ENV') == 'development'

    # Port configuration
    if is_development:
        port = 5002
        debug_mode = True
        print(f"🔧 Development mode: Port {port}")
    else:
        port = int(os.environ.get('PORT', 8080))  # Railway default
        debug_mode = False
        print(f"🚀 Production mode: Port {port}")

    print("Creating Flask app...")
    app = create_app()
    print("Flask app created successfully")

    # Initialize services
    initialize_app_services(app, is_development)

    print(f"Starting Flask server on 0.0.0.0:{port}...")
    app.run(host='0.0.0.0', port=port, debug=debug_mode)

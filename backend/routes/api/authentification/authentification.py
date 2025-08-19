import os
import re

from flask import (
    Blueprint,
    request,
    jsonify
)
from models import User, db
from .utils import (
    hash_password,
    generate_jwt_token,
    verify_password
)
from .middleware import jwt_required
from flask import g

from google_auth_oauthlib.flow import Flow
from google.auth.transport import requests as google_requests
import requests

 

############################ TESTING ############################
import time

############################ ROUTES ############################
# /api/auth:
# /signup
# /login
# /logout
# /me
# /google/login
# /google/callback


############################ IMPLEMENTATION ############################
auth_bp = Blueprint('auth', __name__)


############################ MAIN ROUTES ############################
@auth_bp.route("/signup", methods=["POST"])
def signup():

    print(f"🚨 SIGNUP ROUTE CALLED: {request.method}")
    
    # if request.method == 'OPTIONS':
    #     print("🚨 HANDLING OPTIONS REQUEST")
    #     return '', 200
    
    print("🚨 HANDLING POST REQUEST")

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    email = data.get("email")
    password = data.get("password")
    name = data.get("name")

    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    if '@' not in email:
        return jsonify({"error" : "Invalid email format"}), 400

    if email.count("@") != 1:
        return jsonify({"error" : "Invalid email format"}), 400

    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    if not name:
        return jsonify({"error": "Name is required"}), 400
    
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400
    
    if not any (c.isupper() for c in password):
        return jsonify({
            "error" : "Password must contain at least one uppercase letter"
        }), 400
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\?]', password):
        return jsonify({
            "error" : "Password must contain at least one symbol"
        }), 400

    # VALIDATION PASSED
    # 1. Check if email already exists
    try:
        existing_user = User.query.filter_by(email=email).first()
    except Exception:
        return jsonify({"error": "Database error"}), 500

    if existing_user:
        return jsonify ({
            "error": "Email is already in use"
        }), 400
    try:
        # 2. Hash password
        hashed_password = hash_password(password)

        # 3. Save new User to DB
        new_user = User(
            email=email,
            name=name,
            password_hash=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        # 4. Generate JWT w/ user Id // .id automatically available after commit
        token = generate_jwt_token(new_user.id)

        # 5. Return JWT with user info
        return jsonify ({
            "message": "User created successfully",
            "token": token,
            "user": new_user.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create user"}), 500


@auth_bp.route("/login", methods=["POST"])
def login():
    # Add a timer for testing.
    # time.sleep(3)

    data = request.get_json()

    if not data:
        return jsonify({"error": "No data provided"}), 400

    email = data.get('email')
    password = data.get('password')
    
    if not email:
        return jsonify({"error": "Email is required"}), 400
    
    if not password:
        return jsonify({"error": "Password is required"}), 400
    
    # VALIDATION PASSED
    # 1. Verify email
    try:
        existing_user = User.query.filter_by(email=email).first()
    except Exception:
        return jsonify({"error": "Database error"}), 500
    
    if not existing_user:
        return jsonify({"error": "Invalid credentials"}), 401
    # 2. Verify password and generate JWT
    try:
        if verify_password(password, existing_user.password_hash):
            token = generate_jwt_token(existing_user.id)
            return jsonify ({
                "message": "User logged in successfully",
                "token": token,
                "user": existing_user.to_dict()
            }), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({
        "message": "User logged out"
    }), 200

@auth_bp.route("/me", methods=["GET"])
@jwt_required
def get_current_user():
    user_id = g.current_user_id # Available from middleware

    # Query db
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not present in db"}), 404
    
    return jsonify({
        "user": user.to_dict()
    }), 200


############################ GOOGLE AUTH ROUTES ############################
@auth_bp.route("/google/callback", methods=["POST"])
def google_callback():

    # Take the code from the front.
    data = request.get_json()

    if not data or 'code' not in data:
        return jsonify({"error": "Authorization code is required"}), 400
    
    authorization_code = data.get('code')

    # code from Front exchanged for token
    # Formulate Request.
    # Make a token request to google with formulated Request.
    # Uses flow object. Same as google login
    try:
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                    "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "redirect_uris": ["http://localhost:3000/auth/callback"]
                }
            },
            scopes=[
                "openid", 
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile"
            ]
        )
        flow.redirect_uri = "http://localhost:3000/auth/callback"

        # Exchange authorization code for access token
        # This makes a POST request to Google and the result is stored on
        # flow.credentials.[field] afterwards.
        # All happens over the same HTTP connection. Synchronous.
        flow.fetch_token(code=authorization_code)

        # Now get user info, using the token we got from the code/token exchange
        # Use access token to get user info
        user_info_response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={"Authorization": f"Bearer {flow.credentials.token}"}
        )

        if user_info_response.status_code != 200:
            return jsonify({"error" : "Failed to get user info from Google"}), 400
        
        google_user_data = user_info_response.json()

        # LOGGIN/SIGNIN IN USER.
        # It's one single callback for both.
        google_id = google_user_data['id']
        email = google_user_data['email']
        name = google_user_data['name']

        existing_user = User.query.filter_by(google_id=google_id).first()

        if existing_user:
            user = existing_user
        else:
            # Check if email already exists in DB
            # In this case it would someone signing in with Google, but they 
            # already signed up directly through the website. Would create
            # duplicates in the db.
            email_user = User.query.filter_by(email=email).first()
            if email_user:
                return jsonify({
                    "error" : "Email already registered with regular accoutn"
                }), 400
            else:
                # Create new User in db.
                user = User(
                    email=email,
                    name=name,
                    password_hash=None,
                    google_id=google_id,
                    auth_method="google"
                )
                db.session.add(user)
                db.session.commit()

        # Create JWT. Both cases. Login and SignUp
        token = generate_jwt_token(user.id)

        # time.sleep(3)

        return jsonify ({
            "message": "Google login successful",
            "token": token,
            "user": user.to_dict()
        }), 200

    except Exception as e:
        return jsonify({"error": f"Token exchange failed: {str(e)}"}), 400

@auth_bp.route("/google/login", methods=["GET"])
def google_login():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": ["http://localhost:3000/auth/callback"]
                # Google will redirect to the frontend -> 3000
            }
        },
        scopes=[
            "openid", 
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile"
        ]
    )

    # Set redirect URI
    flow.redirect_uri = "http://localhost:3000/auth/callback"

    # Generate authorization URL
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )

    return jsonify({
        "auth_url": authorization_url,
        "state": state
    })



############################ TESTING ############################
@auth_bp.route("/test")
def test_route():
    return "Authentication Blueprint is working"

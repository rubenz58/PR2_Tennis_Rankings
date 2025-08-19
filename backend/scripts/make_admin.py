#!/usr/bin/env python3
"""
Script to set a user as admin
Usage: python scripts/make_admin.py
"""

import sys
import os

# Add parent directory to path to import Flask app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from models import User, db

def make_admin_by_id(user_id):
    """Set user as admin by ID"""
    app = create_app()
    
    with app.app_context():
        try:
            # Find user by ID
            user = User.query.get(user_id)
            
            if not user:
                print(f"❌ User with ID {user_id} not found")
                return False
            
            # Check current admin status
            if user.is_admin:
                print(f"ℹ️  User {user.email} (ID: {user_id}) is already an admin")
                return True
            
            # Set as admin
            user.is_admin = True
            db.session.commit()
            
            print(f"✅ Successfully set {user.email} (ID: {user_id}) as admin")
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            db.session.rollback()
            return False

def make_admin_by_email(email):
    """Set user as admin by email"""
    app = create_app()
    
    with app.app_context():
        try:
            # Find user by email
            user = User.query.filter_by(email=email).first()
            
            if not user:
                print(f"❌ User with email {email} not found")
                return False
            
            # Check current admin status
            if user.is_admin:
                print(f"ℹ️  User {user.email} (ID: {user.id}) is already an admin")
                return True
            
            # Set as admin
            user.is_admin = True
            db.session.commit()
            
            print(f"✅ Successfully set {user.email} (ID: {user.id}) as admin")
            return True
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            db.session.rollback()
            return False

def list_users():
    """List all users to help find the right ID"""
    app = create_app()
    
    with app.app_context():
        try:
            users = User.query.all()
            print("📋 All users:")
            print("-" * 60)
            for user in users:
                admin_status = "👑 ADMIN" if user.is_admin else "👤 USER"
                print(f"ID: {user.id:2} | {admin_status} | {user.email} | {user.name}")
            print("-" * 60)
            
        except Exception as e:
            print(f"❌ Error listing users: {str(e)}")

if __name__ == '__main__':
    print("🔧 Admin Setup Script")
    print("=" * 40)
    
    # List users first to help you choose
    list_users()
    print()
    
    # SET USER ID HERE
    USER_ID_TO_MAKE_ADMIN = 7
    
    # Or use email instead (comment out the ID line above and uncomment below)
    # USER_EMAIL_TO_MAKE_ADMIN = "your-email@example.com"
    
    # Run the admin setup
    # locals() checks in the local scope
    if 'USER_ID_TO_MAKE_ADMIN' in locals():
        success = make_admin_by_id(USER_ID_TO_MAKE_ADMIN)
    else:
        success = True;
        print("Make Admin by Email attempt")
        # success = make_admin_by_email(USER_EMAIL_TO_MAKE_ADMIN)
    
    if success:
        print("\n🎉 Admin setup complete!")
        print("💡 You can now access admin features with your next login")
    else:
        print("\n💥 Admin setup failed!")
    
    print("\n📋 Updated user list:")
    list_users()
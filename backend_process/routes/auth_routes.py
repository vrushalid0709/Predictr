from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import random
import sys
import os
# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend_process.utils.email_utils import send_otp_email
from backend_process.utils.user_helpers import user_helper
from db_connection.db import db
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

#mongodb collection :users 
users_collection = db['users']
auth = Blueprint('auth', __name__, template_folder='../../public-pages')

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password_input = request.form.get('password')

        # Look up user in the database
        user = users_collection.find_one({"email": email})

        if user:
            # Verify the hashed password
            if check_password_hash(user['password'], password_input):
                # Password is correct - store both email and user_id in session
                session['user'] = email
                session['user_id'] = str(user['_id'])  # Store user_id for stock operations
                flash("Logged in successfully!", "success")
                return redirect(url_for('auth.dashboard'))
            else:
                flash("Invalid credentials. Please check your password.", "danger")
        else:
            flash("User not found. Please sign up.", "warning")

    return render_template('login.html')

# SIGN-UP
@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        # 1️⃣ Check if email is already registered
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            flash("Email is already registered. Please log in instead.", "danger")
            return redirect(url_for('auth.login'))

        #  Hash password before storing in session (more secure)
        hashed_password = generate_password_hash(password)

        #  Store temporary user data in session
        session['temp_user_data'] = {
            "name": name,
            "email": email,
            "password": hashed_password
        }

        #  Generate OTP
        otp_code = str(random.randint(100000, 999999))
        session['otp_code'] = otp_code

        #  Send OTP via email
        send_otp_email(email, name, otp_code)

        flash("An OTP has been sent to your email.", "info")
        return redirect(url_for('otp.verify'))

    return render_template('signup.html')


# DASHBOARD
@auth.route('/dashboard')
def dashboard():
    if 'user' not in session:
        flash("Please log in first", "warning")
        return redirect(url_for('auth.login'))
    
    # Validate user session and get user info
    user_info = user_helper.validate_user_session(session)
    
    if not user_info['valid']:
        flash("Session invalid. Please log in again.", "warning")
        return redirect(url_for('auth.login'))
    
    # Pass both user_name and user_id to the template
    return render_template('dashboard.html', 
                         user_name=user_info['name'], 
                         user_id=user_info['user_id'])


# LOGOUT
@auth.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('user_id', None)  # Also clear user_id
    flash("Logged out successfully!", "success")
    return redirect(url_for('auth.login'))

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from db_connection.db import db
import time
from datetime import datetime
from backend_process.utils.user_helpers import generate_user_id
from backend_process.utils.email_helpers import send_welcome_email

otp = Blueprint('otp', __name__, template_folder='../../public-pages')

users_collection = db['users']
OTP_EXPIRATION_SECONDS = 300

@otp.route('/verify', methods=['GET', 'POST'])
def verify():
    if 'temp_user_data' not in session:
        flash('Please complete the sign-up process first.', 'warning')
        return redirect(url_for('auth.signup'))

    # Check if OTP expired
    if 'otp_timestamp' in session and time.time() - session['otp_timestamp'] > OTP_EXPIRATION_SECONDS:
        session.pop('temp_user_data', None)
        session.pop('otp_code', None)
        session.pop('otp_timestamp', None)
        flash('Your OTP has expired. Please sign up again.', 'warning')
        return redirect(url_for('auth.signup'))

    if request.method == 'POST':
        submitted_otp = ''.join(request.form.get(f'otp_digit{i}', '') for i in range(6))

        if 'otp_code' in session and submitted_otp == session.get('otp_code'):
            user_data = session['temp_user_data']

            # Prevent duplicate email
            if users_collection.find_one({"email": user_data['email']}):
                flash('An account with this email already exists. Please log in.', 'danger')
                session.pop('temp_user_data', None)
                session.pop('otp_code', None)
                session.pop('otp_timestamp', None)
                return redirect(url_for('auth.login'))

            # Generate user ID
            user_id = generate_user_id()

            # Save user to DB
            users_collection.insert_one({
                "user_id": user_id,
                "name": user_data['name'],
                "email": user_data['email'],
                "password": user_data['password'],  # hashed already
                "created_at": datetime.utcnow()
            })

            # Send welcome email
            send_welcome_email(user_data['email'], user_data['name'], user_id)

            # Clear session
            session.pop('temp_user_data', None)
            session.pop('otp_code', None)
            session.pop('otp_timestamp', None)

            flash('Account created successfully! Check your email for a welcome message.', 'success')
            return redirect(url_for('auth.login'))

        else:
            flash('Incorrect verification code. Please try again.', 'danger')

    return render_template('verify_otp.html')

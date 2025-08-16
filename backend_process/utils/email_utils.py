import os
from flask_mail import Message
from backend_process.extensions import mail
from datetime import datetime

def send_otp_email(recipient_email, recipient_name, otp_code):
    """
    Sends a beautifully designed OTP email that matches the website's theme.
    """
    msg = Message(
        subject="Your Predictr Verification Code",
        recipients=[recipient_email]
    )
    
    logo_path = r"H:\Predictr\static\assets\logo_file\png\predictr-high-resolution-logo-transparent.png"
    current_date = datetime.now().strftime("%B %d, %Y")

    # Attach logo if exists
    try:
        with open(logo_path, "rb") as f:
            img_data = f.read()
        msg.attach(
            filename="predictr-logo.png",
            content_type="image/png",
            data=img_data,
            disposition="inline",
            headers={"Content-ID": "<predictr_logo>"}
        )
    except FileNotFoundError:
        print(f"Warning: Logo file not found at {logo_path}")

    # Corrected indentation for HTML assignment
    msg.html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {{
                font-family: 'Poppins', sans-serif;
                background-color: #f6fbff;
                margin: 0;
                padding: 0;
                color: #333333;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 12px;
                padding: 40px;
                box-shadow: 0 8px 30px rgba(0, 122, 51, 0.15);
                text-align: center;
            }}
            .logo {{
                height: 40px;
                margin: 0 auto 15px;
                display: block;
            }}
            .date {{
                text-align: center;
                font-size: 14px;
                color: #888888;
                margin-bottom: 25px;
            }}
            h2 {{
                color: #007a33;
                font-size: 22px;
                margin-bottom: 16px;
            }}
            p {{
                font-size: 15px;
                line-height: 1.6;
                margin-bottom: 20px;
            }}
            .otp-code {{
                display: inline-block;
                background-color: #e0f7f1;
                color: #004d00;
                font-size: 28px;
                font-weight: 700;
                letter-spacing: 4px;
                padding: 15px 30px;
                border-radius: 10px;
                border: 1px solid #007a33;
                margin: 15px 0 20px 0;
            }}
            .footer {{
                margin-top: 30px;
                font-size: 13px;
                color: #666666;
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <img src="cid:predictr_logo" alt="Predictr Logo" class="logo">
            <div class="date">{current_date}</div>

            <h2>Email Verification Required</h2>
            <p>Hello <strong>{recipient_name}</strong>,</p>
            <p>Thank you for joining <b>Predictr</b>! To keep your account secure, please verify your email using the one-time code below:</p>
            
            <div class="otp-code">{otp_code}</div>
            
            <p>This code is valid for <strong>5 minutes</strong>. Please enter it on the verification page to complete your signup.</p>

            <div class="footer">
                <p>If you did not request this, you can safely ignore this email.</p>
                <p>— The Predictr Team</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Send the email
    try:
        mail.send(msg)
        print(f"OTP email sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Error sending email: {e}")

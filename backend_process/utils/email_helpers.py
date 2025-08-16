import os
from flask_mail import Message
from backend_process.extensions import mail
from datetime import datetime


def send_welcome_email(email, name, user_id):
    """
    Sends a warm, beautifully designed welcome email matching the website's theme.
    """
    msg = Message(
        subject="Welcome to Predictr! 🎉",
        recipients=[email]
    )

   
    try:
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        logo_path = os.path.join(base_dir, 'static', 'assets', 'logo_file', 'png', 'predictr-high-resolution-logo-transparent.png')

        with open(logo_path, 'rb') as f:
            img_data = f.read()

        msg.attach(
            filename="predictr_logo.png",
            content_type="image/png",
            data=img_data,
            disposition="inline",
            headers={"Content-ID": "<predictr_logo>"}
        )
        current_date = datetime.now().strftime("%B %d, %Y")

    except FileNotFoundError:
        print("Warning: Logo file not found. Email will be sent without logo.")

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
        }}
        .logo {{
            height: 40px;
            margin: 0 auto 20px;
            display: block;
        }}
        .date {{
            text-align: center;
            font-size: 14px;
            color: #888888;
            margin-bottom: 30px;
        }}
        h2 {{
            font-size: 22px;
            margin-bottom: 16px;
            color: #007a33;
            text-align: center;
        }}
        p {{
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 20px;
        }}
        .steps {{
            margin: 25px 0;
            padding: 20px;
            background-color: #e0f7f1;
            border-left: 4px solid #007a33;
            border-radius: 8px;
        }}
        .steps p {{
            font-weight: 600;
            margin-bottom: 12px;
            color: #004d00;
        }}
        .steps ul {{
            padding-left: 20px;
            margin: 0;
        }}
        .steps li {{
            margin-bottom: 10px;
            font-size: 14px;
            color: #333333;
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


        <h2>Welcome to Predictr, {name}! 🎉</h2>

        <p>We’re so glad you’ve joined us! At <b>Predictr</b>, our mission is to make the stock market more 
        understandable, approachable, and engaging for everyone — whether you’re just getting started 
        or looking to sharpen your investing skills.</p>

        <p>Predictr brings together powerful tools and a simple, user-friendly interface to help you learn and explore:</p>

        <div class="steps">
            <p>Here’s what you can do with Predictr:</p>
            <ul>
                <li><b>Secure Login:</b> Access your personalized dashboard anytime.</li>
                <li><b>Pick Your Stocks:</b> Explore popular companies like AAPL, TSLA, and more.</li>
                <li><b>Visualize Trends:</b> Interactive charts show past performance.</li>
                <li><b>Predict Prices:</b> Our ML-powered model forecasts the next 7 days.</li>
                <li><b>Simulate Investments:</b> Test “what if” scenarios with virtual money.</li>
                <li><b>Learn with Our Assistant:</b> A friendly chatbot guides you step by step.</li>
            </ul>
        </div>

        <p>We’re here to support your journey towards smarter financial decisions. 
        Your dashboard is ready — log in and start exploring today!</p>

        <div class="footer">
            <p>Warm regards,<br><b>The Predictr Team</b></p>
        </div>
    </div>
</body>
</html>
"""


    try:
        mail.send(msg)
        print(f"Welcome email sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send welcome email to {email}: {e}")

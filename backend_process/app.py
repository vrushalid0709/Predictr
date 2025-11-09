from flask import Flask, render_template
from dotenv import load_dotenv
import os
import sys
from flask import Blueprint
from flask_cors import CORS


# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend_process.extensions import mail
from backend_process.routes.FetchStock import fetch_stock
from backend_process.routes.StockRoutes import stock_routes
from .train_model import train_lstm_model
from .predict_stock import predict_stock_price
from backend_process.routes.predict_route import predict_bp


load_dotenv()

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'public-pages'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)
CORS(app)

app.secret_key = os.getenv("SECRET_KEY")

# Flask-Mail config
app.config['MAIL_SERVER'] = os.getenv("MAIL_SERVER")
app.config['MAIL_PORT'] = int(os.getenv("MAIL_PORT"))
app.config['MAIL_USE_TLS'] = os.getenv("MAIL_USE_TLS") == "True"
app.config['MAIL_USERNAME'] = os.getenv("MAIL_USERNAME")
app.config['MAIL_PASSWORD'] = os.getenv("MAIL_PASSWORD")
app.config['MAIL_DEFAULT_SENDER'] = os.getenv("MAIL_DEFAULT_SENDER")

mail.init_app(app)

# Import blueprints AFTER extensions are initialized
from backend_process.routes.auth_routes import auth
from backend_process.routes.otp_routes import otp
from backend_process.routes.gemini_routes import gemini_bp
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(otp, url_prefix='/otp')
app.register_blueprint(fetch_stock, url_prefix='/api')
app.register_blueprint(stock_routes, url_prefix="/api")
app.register_blueprint(gemini_bp, url_prefix="/api")
app.register_blueprint(predict_bp)


# page routes to frontend 
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup-page')
def signup_page():
    return render_template('signup.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

# Dashboard placeholder
dashboard = Blueprint('dashboard', __name__)
@dashboard.route('/view')
def view():
    from flask import session, redirect, url_for, flash
    # Check if user is logged in
    if 'user' not in session:
        flash("Please log in first", "warning")
        return redirect(url_for('auth.login'))
    
    # Validate user session and get user info
    from backend_process.utils.user_helpers import user_helper
    user_info = user_helper.validate_user_session(session)
    
    if not user_info['valid']:
        flash("Session invalid. Please log in again.", "warning")
        return redirect(url_for('auth.login'))
    
    # Pass both user_name and user_id to the template
    return render_template('dashboard.html', 
                         user_name=user_info['name'], 
                         user_id=user_info['user_id'])
app.register_blueprint(dashboard, url_prefix='/dashboard')

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/api/stocks/predict", methods=["POST"])
def predict_stock(symbol):
    return predict_stock(symbol)


# Run app
if __name__ == "__main__":
    app.run(debug=True)

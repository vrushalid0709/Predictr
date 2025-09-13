from flask import Flask, render_template
from dotenv import load_dotenv
import os
from flask import Blueprint
from backend_process.extensions import mail
from backend_process.routes.FetchStock import fetch_stock

load_dotenv()

app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'public-pages'),
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'static')
)

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
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(otp, url_prefix='/otp')
app.register_blueprint(fetch_stock, url_prefix='/api')

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
    return render_template('dashboard.html')
app.register_blueprint(dashboard, url_prefix='/dashboard')

@app.route("/contact")
def contact():
    return render_template("contact.html")

# Run app
if __name__ == "__main__":
    app.run(debug=True)

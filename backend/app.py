from flask import Flask, render_template, request, redirect, url_for
from config import Config
from email_sender import send_email
from tasks import schedule_email
from database import db, EmailStatus

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.route('/')
def dashboard():
    email_statuses = EmailStatus.query.all()
    return render_template('dashboard.html', email_statuses=email_statuses)

@app.route('/send_email', methods=['POST'])
def send_email_route():
    email_data = request.form.get('email_data')
    # Add logic to handle email sending or scheduling
    schedule_email.apply_async(args=[email_data], countdown=60)  # Schedule after 1 minute
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, request, jsonify
from email_service import send_email, schedule_emails
from db_setup import setup_db

app = Flask(__name__)

setup_db()

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    file.save('uploaded_data.csv')
    return jsonify({"message": "File uploaded successfully!"})

@app.route('/send-email', methods=['POST'])
def send_email_route():
    data = request.json
    result = send_email(data)
    return jsonify({"message": "Emails sent!", "result": result})

@app.route('/schedule-email', methods=['POST'])
def schedule_email_route():
    data = request.json
    schedule_emails(data)
    return jsonify({"message": "Emails scheduled!"})

if __name__ == '__main__':
    app.run(debug=True)

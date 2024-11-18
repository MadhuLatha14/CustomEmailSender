import smtplib
from email.mime.text import MIMEText
import schedule
import time
import sqlite3

def send_email(data):
    conn = sqlite3.connect('email_data.db')
    cursor = conn.cursor()

    results = []
    smtp_server = smtplib.SMTP('smtp.gmail.com', 587)
    smtp_server.starttls()
    smtp_server.login(data['email'], data['password'])

    for row in data['emails']:
        msg = MIMEText(row['body'])
        msg['Subject'] = row['subject']
        msg['From'] = data['email']
        msg['To'] = row['to']

        try:
            smtp_server.sendmail(data['email'], row['to'], msg.as_string())
            results.append({'email': row['to'], 'status': 'Sent'})
            cursor.execute("INSERT INTO email_status (email, status) VALUES (?, ?)", (row['to'], 'Sent'))
        except Exception as e:
            results.append({'email': row['to'], 'status': 'Failed', 'error': str(e)})
            cursor.execute("INSERT INTO email_status (email, status) VALUES (?, ?)", (row['to'], 'Failed'))

    conn.commit()
    conn.close()
    smtp_server.quit()
    return results

def schedule_emails(data):
    for row in data['emails']:
        schedule.every(data['interval']).seconds.do(send_email, {'emails': [row], 'email': data['email'], 'password': data['password']})

    while True:
        schedule.run_pending()
        time.sleep(1)

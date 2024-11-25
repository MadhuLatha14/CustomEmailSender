import pandas as pd
from SendgridEmailSender import EmailSender
from GrokMessageGenerator import GrokMessageGenerator

import datetime
import time
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
import gradio as gr
import threading

#tracks the jobs in the queue to display in progress bar in email sender tab
class JobTracker:
    def __init__(self):
        self.total_jobs = 0
        self.completed_jobs = 0
        self.lock = threading.Lock()
    
    def reset(self):
        with self.lock:
            self.total_jobs = 0
            self.completed_jobs = 0
    
    def increment_completed(self):
        with self.lock:
            self.completed_jobs += 1
    
    def get_progress(self):
        with self.lock:
            if self.total_jobs == 0:
                return 0
            return (self.completed_jobs / self.total_jobs) * 100

job_tracker = JobTracker()
email_sender = EmailSender()
llm_message_generator = GrokMessageGenerator()

#wrapper to track the jobs
def send_email_with_tracking(email, subject, message, personalisation_dict):
    try:
        email_sender.send_email(email, subject, message, personalisation_dict)
    finally:
        job_tracker.increment_completed()

#format the user input with the placeholders in the data
def create_prompt(row, user_prompt):
    # user_prompt = f"Generate an email selling my marketing services to this company {company} located at {location} which sells these {products}"
    user_prompt_formatted = user_prompt.format(**row)
    return user_prompt_formatted

#should come from llm
def generate_message(prompt):
    generated_message = llm_message_generator.get_ai_message(prompt)
    return generated_message

#convert the scheduled time to unix timestamp
def get_unix_timestamp(scheduled_at):
    datetime_string = scheduled_at

    # Parse the string into a datetime object
    datetime_obj = datetime.strptime(datetime_string, "%Y-%m-%d %H:%M:%S")

    # Convert to UNIX timestamp
    unix_timestamp = int(datetime_obj.timestamp())
    return unix_timestamp

#update the email into the database
def insert_email(company_name, email_id):
    email_details = {
        "company_name": company_name,
        "email_id": email_id,  # The unique email ID
        "sg_message_id": None,  # sg_message_id will be updated later
        "status": "Scheduled",  # Initial status
    }

    result = email_sender.emails_collection.insert_one(email_details)
    print(f"Email inserted with ID: {result.inserted_id}")

#process the data from the csv file
def process_data(file=None, subject = None, user_prompt = None, scheduling = False, scheduled_at=None, throttling = False, max_emails_per_hour = None, progress = gr.Progress()):
    
    if scheduled_at:
        unix_timestamp = get_unix_timestamp(scheduled_at)
    if file is None:
        file = open('company_data.csv', 'r')
    df = pd.read_csv(file.name)
    job_tracker.reset()
    job_tracker.total_jobs = len(df)
    
    # Initial setup progress
    progress(0, desc="Initializing...")
    time.sleep(1)  # Give users time to see the initialization

    THROTTLE_DELAY  = 3600 / max_emails_per_hour if throttling else 0
    scheduler = BackgroundScheduler()
       
    for idx, row in df.iterrows():
         # Show progress for scheduling phase
        schedule_progress = (idx + 1) / len(df) * 0.2  # First 20% is for scheduling
        progress(schedule_progress, desc=f"Scheduling email {idx + 1} of {len(df)}...")
        
        email = row['Email']
        company_name = row["Company Name"]

        insert_email(company_name, email) # Insert email into the database
        prompt = create_prompt(row, user_prompt=user_prompt)
        message = generate_message(prompt)
        scheduled_time = unix_timestamp if scheduled_at else None
        personalisation_dict = {"send_at": scheduled_time}
                
        run_time = (datetime.strptime(scheduled_at, "%Y-%m-%d %H:%M:%S") if scheduling else datetime.now()) + timedelta(seconds= idx * THROTTLE_DELAY)
        scheduler.add_job(send_email_with_tracking, args=[email, subject, message, personalisation_dict], run_date=run_time, misfire_grace_time=30)
    scheduler.start()

    #keep program running while there are jobs in the scheduler
    try:
         while len(scheduler.get_jobs()) > 0:
            completed = job_tracker.completed_jobs
            total = job_tracker.total_jobs
            execution_progress = 0.2 + (completed / total * 0.8)  # Remaining 80% is for execution
            
            status = "✓ Scheduled  |  " if scheduling else ""
            if completed == total:
                status += "✓ All emails sent!"
            else:
                status += f"Sending: {completed}/{total} emails"
                if throttling:
                    status += f" (max {max_emails_per_hour}/hour)"
            
            progress(execution_progress, desc=status)
            time.sleep(1)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        return "Process interrupted!"
    finally:
        scheduler.shutdown()
    
    return f"Success! Sent {job_tracker.completed_jobs} emails."

if __name__ == "__main__":
    
    #this is old and needs to be changed
    process_data(user_prompt="Generate an email to {Company Name} located at {Location} promoting my marketing services to them, emphasizing my experience in selling {Products}.", 
                 scheduled_at="2024-11-8 23:37:00",
                 max_emails_per_hour=10)

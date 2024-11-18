import sendgrid
from sendgrid.helpers.mail import Mail
from config import Config
import openai

# Initialize OpenAI API Key
openai.api_key = Config.OPENAI_API_KEY

def generate_email_content(prompt, data):
    # Replace placeholders in the prompt with actual data
    filled_prompt = prompt.format(**data)
    
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=filled_prompt,
        max_tokens=150
    )
    
    return response.choices[0].text.strip()


def send_email(to_email, subject, content):
    sg = sendgrid.SendGridAPIClient(api_key=Config.SENDGRID_API_KEY)
    message = Mail(
        from_email='your-email@example.com',
        to_emails=to_email,
        subject=subject,
        html_content=content)
    try:
        response = sg.send(message)
        return response.status_code
    except Exception as e:
        print(e.message)
        return None

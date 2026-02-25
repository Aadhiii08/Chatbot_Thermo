import os
from dotenv import load_dotenv

load_dotenv()

from utils import send_email_with_attachment

success = send_email_with_attachment(
    receiver_email="test@example.com",
    subject="Test email from backend",
    body="This is a test to verify if Mailjet is actually working."
)

print(f"Status: {success}")

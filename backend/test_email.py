import os
from dotenv import load_dotenv
from utils import send_email_with_attachment

load_dotenv()

def test_smtp_connection():
    receiver_email = "mgmt@dmthermoformer.com"  # Using the same email for testing to themselves
    subject = "SMTP Test Email"
    body = "This is a test email sent using smtplib to verify the direct email connection."

    print("Testing direct SMTP email sending...")
    success = send_email_with_attachment(receiver_email, subject, body)
    
    if success:
        print("[+] Test email sent successfully!")
    else:
        print("[-] Failed to send test email.")

if __name__ == "__main__":
    test_smtp_connection()

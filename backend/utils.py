import os
import smtplib
from email.message import EmailMessage
from email.utils import make_msgid
import mimetypes

def send_email_with_attachment(receiver_email, subject, body, attachment_paths=None):
    # Load keys
    smtp_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_PORT", 465))
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")

    if not sender_email or not sender_password:
        print("[X] Error: SMTP Credentials (EMAIL_ADDRESS or EMAIL_PASSWORD) are missing.")
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = f"DM Thermoformer <{sender_email}>"
    msg['To'] = receiver_email
    
    # We use add_alternative to send as HTML
    msg.add_alternative(f"<p>{body.replace(chr(10), '<br>')}</p>", subtype='html')

    # helper to handle single path or list
    paths = []
    if attachment_paths:
        if isinstance(attachment_paths, str):
            paths = [attachment_paths]
        elif isinstance(attachment_paths, list):
            paths = attachment_paths
            
    for path in paths:
        if path and os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    file_data = f.read()
                
                mime_type, _ = mimetypes.guess_type(path)
                if mime_type is None:
                    mime_type = 'application/octet-stream'
                maintype, subtype = mime_type.split('/', 1)
                
                msg.add_attachment(file_data, maintype=maintype, subtype=subtype, filename=os.path.basename(path))
            except Exception as e:
                print(f"[!] Error preparing attachment {path}: {e}")

    try:
        print(f"[*] Sending email via SMTP to {receiver_email}...")
        
        # Connect to server
        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_host, smtp_port)
        else:
            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"[+] Email sent successfully via SMTP!")
        return True
    except Exception as e:
        print(f"[-] SMTP Email Request Failed: {e}")
        return False
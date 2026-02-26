import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

def send_email_with_attachment(receiver_email, subject, body, attachment_paths=None):
    # Load credentials
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    smtp_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("EMAIL_PORT", 465))

    if not sender_email or not sender_password:
        print("[X] Error: Email credentials are missing.")
        return False

    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = f"DM Thermoformer <{sender_email}>"
    msg['To'] = receiver_email
    msg['Subject'] = subject

    # Attach the body text as HTML
    html_body = f"<p>{body.replace(chr(10), '<br>')}</p>"
    msg.attach(MIMEText(html_body, 'html'))

    # Attach any provided files
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
                    part = MIMEApplication(f.read(), Name=os.path.basename(path))
                
                # Add headers for the attachment
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(path)}"'
                msg.attach(part)
            except Exception as e:
                print(f"[!] Error preparing attachment {path}: {e}")

    # Send the email
    try:
        print(f"[*] Sending email via SMTP ({smtp_host}:{smtp_port}) to {receiver_email}...")
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.login(sender_email, sender_password)
                server.send_message(msg)
                
        print(f"[+] Email sent successfully to {receiver_email}!")
        return True
    except Exception as e:
        print(f"[-] Failed to send email via SMTP: {e}")
        return False
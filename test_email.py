"""Manual-only email delivery test. Never claims stock availability."""
import os
import smtplib
from email.message import EmailMessage

def main():
    sender = os.environ.get("GMAIL_ADDRESS", "")
    password = os.environ.get("GMAIL_APP_PASSWORD", "")
    if sender != "nickysuning@gmail.com" or not password:
        raise SystemExit("Gmail secrets missing or sender does not match configured account.")
    message = EmailMessage()
    message["From"] = sender
    message["To"] = "nickysu@126.com"
    message["Subject"] = "TEST ONLY - Sydney Apple stock checker"
    message.set_content("This is a one-off delivery test, not a stock notification.")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=20) as smtp:
        smtp.login(sender, password)
        smtp.send_message(message)
    print("Gmail accepted test email for delivery to nickysu@126.com.")

if __name__ == "__main__":
    main()

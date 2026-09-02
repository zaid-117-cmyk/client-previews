import os
import time
import imaplib
import smtplib
import email
from email.message import EmailMessage
import subprocess
import argparse

def check_for_replies(imap_server, email_user, email_pass):
    print(f"Connecting to IMAP server {imap_server}...")
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select("inbox")
        
        # Search for unseen emails with "Yes" or related intent
        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()
        
        # Load Whitelist
        whitelist_emails = set()
        log_path = "dashboard/data/campaign_log.json"
        if os.path.exists(log_path):
            import json
            try:
                with open(log_path, 'r') as f:
                    logs = json.load(f)
                    for log in logs:
                        whitelist_emails.add(log.get("email", "").lower())
            except Exception as e:
                print(f"Error reading whitelist: {e}")

        prospects_to_process = []
        
        for e_id in email_ids:
            _, msg_data = mail.fetch(e_id, '(RFC822)')
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    subject = msg["subject"]
                    sender = msg["from"]
                    
                    # Extract body (simplistic for demo)
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    # STRICT FILTER: Check if email is in whitelist
                    sender_email = sender.split('<')[-1].strip('>').lower()
                    if sender_email not in whitelist_emails:
                        continue

                    # Check subject match
                    subject_lower = str(subject).lower() if subject else ""
                    is_campaign_reply = "quick question regarding" in subject_lower

                    if is_campaign_reply and ("yes" in body.lower() or "sure" in body.lower() or "send" in body.lower()):
                        print(f"Found positive lead reply from {sender}. Subject: {subject}")
                        business_name = sender.split('<')[0].strip() or "Prospect Business"
                        
                        # Use Gemini to Score the Lead
                        score = "WARM"
                        import google.generativeai as genai
                        api_key = os.getenv("GEMINI_API_KEY")
                        if api_key:
                            try:
                                genai.configure(api_key=api_key)
                                model = genai.GenerativeModel('gemini-1.5-flash')
                                prompt = f"Analyze this reply to a cold email: '{body}'. Rate the lead's intent as HOT, WARM, or COLD. Return ONLY the single word."
                                response = model.generate_content(prompt)
                                score = response.text.strip().upper()
                                if score not in ["HOT", "WARM", "COLD"]: score = "WARM"
                            except Exception: pass

                        prospects_to_process.append({
                            "email": sender_email,
                            "business_name": business_name,
                            "city": "Unknown City",
                            "score": score
                        })
        mail.close()
        mail.logout()
        return prospects_to_process
    except Exception as e:
        print(f"IMAP Error: {e}")
        return []

def send_demo_link(smtp_server, smtp_port, email_user, email_pass, to_email, business_name, demo_url, sender_alias=None):
    print(f"Sending demo link to {to_email}...")
    msg = EmailMessage()
    msg['Subject'] = f"Re: Quick question regarding {business_name}'s website"
    msg['From'] = sender_alias or email_user
    msg['To'] = to_email
    
    body = f"""Hi there,

Here is the live interactive prototype I built for {business_name}:
{demo_url}

A few things I specifically improved:
1. Fast mobile-first layout with instant appointment request buttons.
2. Clean service showcase with modern trust badges and patient review cards.

If you like the direction and want to make this your official website (or tweak anything), feel free to grab a quick 10-minute chat with me:
https://cal.com/your-agency/15min

Hope you like it!

Best,
Web Design & Growth Strategist
"""
    msg.set_content(body)
    
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
        print("Email sent successfully!")
    except Exception as e:
        print(f"SMTP Error: {e}")

def run_auto_responder():
    imap_server = os.getenv("IMAP_SERVER", "imap.gmail.com")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "465"))
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    github_username = os.getenv("GITHUB_USERNAME", "your-username")
    
    if not email_user or not email_pass:
        print("Missing EMAIL_USER or EMAIL_PASS environment variables.")
        return
        
    prospects = check_for_replies(imap_server, email_user, email_pass)
    
    for prospect in prospects:
        name = prospect["business_name"]
        city = prospect["city"]
        score = prospect.get("score", "WARM")
        
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

        # Write score.json so generate_preview commits it
        import json
        os.makedirs(f"previews/{slug}", exist_ok=True)
        with open(f"previews/{slug}/score.json", "w") as f:
            json.dump({"score": score}, f)

        # 1. Call generate_preview.py
        print(f"Generating preview for {name}...")
        subprocess.run(["python", "scripts/generate_preview.py", "--name", name, "--city", city, "--auto-commit"])
        demo_url = f"https://elevateweb.me/client-previews/previews/{slug}/"
        
        # 3. Send Email
        sender_alias = os.getenv("SENDER_ALIAS", "hello@elevateweb.me")
        send_demo_link(smtp_server, smtp_port, email_user, email_pass, prospect["email"], name, demo_url, sender_alias)

if __name__ == "__main__":
    run_auto_responder()

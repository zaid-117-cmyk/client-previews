import os
import time
import imaplib
import smtplib
import email
from email.message import EmailMessage
import subprocess
import argparse

def load_env():
    env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_file):
        try:
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        k, v = line.split('=', 1)
                        k, v = k.strip(), v.strip().strip('"').strip("'")
                        if k not in os.environ:
                            os.environ[k] = v
        except Exception:
            pass

load_env()

def check_for_replies(imap_server, email_user, email_pass):
    print(f"Connecting to IMAP server {imap_server}...")
    try:
        mail = imaplib.IMAP4_SSL(imap_server)
        mail.login(email_user, email_pass)
        mail.select("inbox")
        
        # Search for unseen emails with "Yes" or related intent
        status, messages = mail.search(None, '(UNSEEN)')
        email_ids = messages[0].split()
        
        # Load Whitelist and metadata
        whitelist_data = {}
        log_path = "dashboard/data/campaign_log.json"
        if os.path.exists(log_path):
            import json
            try:
                with open(log_path, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
                    for log in logs:
                        e = log.get("email", "").strip().lower()
                        if e:
                            whitelist_data[e] = log
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
                    
                    # Extract body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors='ignore')
                                break
                    else:
                        payload = msg.get_payload(decode=True)
                        body = payload.decode(errors='ignore') if payload else ""
                    
                    # STRICT FILTER: Check if email is in whitelist
                    sender_email = sender.split('<')[-1].strip('>').strip().lower()
                    if sender_email not in whitelist_data:
                        continue

                    # Check subject match & positive intent
                    subject_lower = str(subject).lower() if subject else ""
                    is_campaign_reply = any(k in subject_lower for k in ["quick question", "regarding", "free", "website"]) or subject_lower.startswith("re:")

                    positive_keywords = ["yes", "sure", "send", "link", "love to", "show me", "check", "interested", "please", "ok", "yeah"]
                    is_positive = any(kw in body.lower() for kw in positive_keywords)

                    if is_campaign_reply and is_positive:
                        lead_info = whitelist_data[sender_email]
                        business_name = lead_info.get("company") or sender.split('<')[0].strip() or "Prospect Business"
                        city = lead_info.get("city") or "Miami, FL"
                        first_name = lead_info.get("first_name") or "there"

                        print(f"Found positive lead reply from {sender} ({business_name}, {city}). Subject: {subject}")
                        
                        # Use Gemini 3.6 Flash to Score the Lead
                        score = "WARM"
                        api_key = os.getenv("GEMINI_API_KEY")
                        if api_key:
                            try:
                                import urllib.request
                                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
                                prompt_text = f"Analyze this reply to a cold email: '{body}'. Rate the lead's intent as HOT, WARM, or COLD. Return ONLY the single word."
                                req_data = json.dumps({"contents": [{"parts": [{"text": prompt_text}]}]}).encode('utf-8')
                                req = urllib.request.Request(url, data=req_data, headers={'Content-Type': 'application/json'})
                                with urllib.request.urlopen(req, timeout=15) as resp:
                                    res_json = json.loads(resp.read().decode('utf-8'))
                                    gemini_text = res_json['candidates'][0]['content']['parts'][0]['text'].strip().upper()
                                    for s in ["HOT", "WARM", "COLD"]:
                                        if s in gemini_text:
                                            score = s
                                            break
                            except Exception as ex:
                                print(f"Scoring note: {ex}")

                        prospects_to_process.append({
                            "email": sender_email,
                            "business_name": business_name,
                            "city": city,
                            "first_name": first_name,
                            "score": score
                        })
        mail.close()
        mail.logout()
        return prospects_to_process
    except Exception as e:
        print(f"IMAP Error: {e}")
        return []

def send_demo_link(smtp_server, smtp_port, email_user, email_pass, to_email, business_name, demo_url, sender_alias=None, first_name=None):
    print(f"Sending demo link to {to_email}...")
    msg = EmailMessage()
    msg['Subject'] = f"Re: Quick question regarding {business_name}'s website"
    msg['From'] = sender_alias or email_user
    msg['To'] = to_email
    
    greeting = f"Hi {first_name}" if first_name and first_name.lower() != "there" else "Hi there"
    
    body = f"""{greeting},

Here is the live interactive prototype I built for {business_name}:
{demo_url}

A few things I specifically improved:
1. Fast mobile-first layout with instant appointment request buttons.
2. Clean service showcase with modern trust badges and client review cards.

If you like the direction and want to make this your official website (or tweak anything), feel free to shoot me a message on WhatsApp:
https://wa.me/918369655161

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
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not email_user or not email_pass:
        print("Missing EMAIL_USER or EMAIL_PASS environment variables.")
        return
        
    prospects = check_for_replies(imap_server, email_user, email_pass)
    
    for prospect in prospects:
        name = prospect["business_name"]
        city = prospect["city"]
        first_name = prospect.get("first_name", "there")
        score = prospect.get("score", "WARM")
        
        import re
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')

        # Write score.json so generate_preview commits it
        import json
        os.makedirs(f"previews/{slug}", exist_ok=True)
        with open(f"previews/{slug}/score.json", "w", encoding='utf-8') as f:
            json.dump({"score": score}, f, indent=2)

        # 1. Call generate_preview.py with proper company name, city, and API key
        print(f"Generating preview for {name} ({city})...")
        subprocess.run(["python", "scripts/generate_preview.py", "--name", name, "--city", city, "--api-key", api_key, "--auto-commit"])
        demo_url = f"https://elevateweb.me/client-previews/previews/{slug}/"
        
        # 2. Send Email
        sender_alias = os.getenv("SENDER_ALIAS", "hello@elevateweb.me")
        send_demo_link(smtp_server, smtp_port, email_user, email_pass, prospect["email"], name, demo_url, sender_alias, first_name)

if __name__ == "__main__":
    run_auto_responder()

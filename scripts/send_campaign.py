import csv
import smtplib
import time
from email.message import EmailMessage
import os
import json
from datetime import datetime

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

# --- Configuration ---
CSV_FILE = "leads.csv"
SENDER_EMAIL = os.getenv("EMAIL_USER", "shehajj17@gmail.com")
APP_PASSWORD = os.getenv("EMAIL_PASS", "gxtdyrommghengck")
SENDER_ALIAS = os.getenv("SENDER_ALIAS", "hello@elevateweb.me")
# ---------------------

def send_campaign():
    if not os.path.exists(CSV_FILE):
        print(f"Error: Could not find {CSV_FILE}. Please make sure your CSV is in the same folder as this script.")
        return

    # Connect to Gmail SMTP
    print("Connecting to Gmail...")
    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(SENDER_EMAIL, APP_PASSWORD)
    except Exception as e:
        print(f"Failed to connect to Gmail. Did you put in the correct App Password? Error: {e}")
        return

    success_count = 0

    with open(CSV_FILE, mode='r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        
        for row_raw in reader:
            # Create a case-insensitive dictionary for easy lookup
            row = {k.strip().lower(): v for k, v in row_raw.items() if k}
            
            # Try to grab the data using common Apollo CSV column names
            email = row.get("email")
            first_name = row.get("first name", "there")
            company = row.get("company", row.get("company name for emails", "your company"))
            city = row.get("city", "your city")

            if not email:
                continue

            print(f"Drafting email to {first_name} at {company} ({email})...")

            msg = EmailMessage()
            msg['Subject'] = f"Quick question regarding {company}'s website"
            msg['From'] = SENDER_ALIAS
            msg['To'] = email
            
            body = f"""Hi {first_name},

I have made a luxurious website for {company}, do you wanna have a look? Drop a yes.

Zaid 
ElevateWeb

Sent From my IPHONE
"""
            msg.set_content(body)

            try:
                server.send_message(msg)
                print(f"  -> Sent successfully to {email}!")
                success_count += 1

                # Log to dashboard
                log_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard', 'data', 'campaign_log.json')
                try:
                    with open(log_path, 'r') as f:
                        log_data = json.load(f)
                except (FileNotFoundError, json.JSONDecodeError):
                    log_data = []
                
                log_data.append({
                    "email": email,
                    "first_name": first_name,
                    "company": company,
                    "city": city,
                    "sent_at": datetime.now().isoformat()
                })
                
                os.makedirs(os.path.dirname(log_path), exist_ok=True)
                with open(log_path, 'w') as f:
                    json.dump(log_data, f, indent=2)

                # Wait 10 seconds between emails so Google doesn't think you are a spam bot
                time.sleep(10) 
            except Exception as e:
                print(f"  -> Failed to send to {email}: {e}")

    server.quit()
    print(f"\nCampaign Complete! Successfully sent {success_count} emails.")

    print("Syncing whitelist to GitHub for AI Auto-Responder...")
    try:
        import subprocess
        log_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dashboard', 'data', 'campaign_log.json')
        subprocess.run(["git", "add", log_file], check=True, cwd=os.path.dirname(log_file))
        subprocess.run(["git", "commit", "-m", "Auto-sync campaign whitelist"], cwd=os.path.dirname(log_file))
        subprocess.run(["git", "push"], check=True, cwd=os.path.dirname(log_file))
        print("Whitelist synced successfully.")
    except Exception as e:
        print(f"Failed to sync whitelist to GitHub: {e}")

if __name__ == "__main__":
    send_campaign()

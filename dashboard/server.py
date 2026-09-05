from flask import Flask, jsonify, request, send_from_directory
import os
import json
import imaplib
import email
from email.header import decode_header
import google.generativeai as genai
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))
import agent_scraper
app = Flask(__name__, static_folder='.', static_url_path='')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/chat_history', methods=['GET'])
def get_chat_history():
    target_email = request.args.get('email', '').strip().lower()
    if not target_email:
        return jsonify({"error": "No email provided"}), 400
    
    # Try environment variables first, then fallback to known local config
    email_user = os.getenv("EMAIL_USER", "shehajj17@gmail.com")
    email_pass = os.getenv("EMAIL_PASS", "gxtdyrommghengck")
    
    messages = []
    try:
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(email_user, email_pass)
        
        # Select All Mail if possible, otherwise INBOX
        try:
            mail.select('"[Gmail]/All Mail"')
        except:
            mail.select('inbox')
            
        # Search for emails TO or FROM the target
        status, response = mail.search(None, f'OR FROM "{target_email}" TO "{target_email}"')
        
        if status == 'OK' and response[0]:
            email_ids = response[0].split()
            # Fetch last 5 emails to be fast
            for e_id in email_ids[-5:]:
                res, msg_data = mail.fetch(e_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        
                        subject, encoding = decode_header(msg.get("Subject", ""))[0]
                        if isinstance(subject, bytes): 
                            subject = subject.decode(encoding or 'utf-8', errors='ignore')
                        
                        sender = msg.get("From", "")
                        
                        body = ""
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode(errors='ignore')
                                    break
                        else:
                            body = msg.get_payload(decode=True).decode(errors='ignore')
                        
                        is_me = email_user.lower() in sender.lower() or "elevateweb.me" in sender.lower()
                        messages.append({
                            "sender": "Me" if is_me else "Client",
                            "subject": subject,
                            "body": body.strip()[:600] + ("..." if len(body)>600 else ""),
                            "is_me": is_me
                        })
        mail.close()
        mail.logout()
    except Exception as e:
        print(f"IMAP Error: {e}")
        return jsonify({"error": str(e)}), 500
        
    return jsonify({"messages": messages})

import urllib.request

@app.route('/api/prospector', methods=['POST'])
def prospector():
    data = request.json or {}
    niche = data.get('niche', 'Yacht Charters')
    city = data.get('city', 'Miami')
    
    # Avoid hardcoding secrets; load from environment or config
    api_key = os.environ.get('GROQ_API_KEY')
    if not api_key:
        return jsonify({"error": "Groq API key not configured on server"}), 500
        
    try:
        url = "https://api.groq.com/openai/v1/chat/completions"
        prompt = f"I am a web design agency looking for clients. Generate an exact Apollo.io Boolean search string to find '{niche}' business owners (CEO, Founder, Owner) in '{city}'. Then, generate 3 highly creative Google Search queries (using operators like inurl: or intitle:) to scrape leads. Keep the response clean and formatted with bullet points."
        
        payload = {
            "model": "openai/gpt-oss-20b",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json'
            }
        )
        
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            result_text = res_data['choices'][0]['message']['content']
            
        return jsonify({"result": result_text})
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'read'):
            try:
                error_msg = e.read().decode('utf-8')
            except:
                pass
        print(f"Groq API Error: {error_msg}")
        return jsonify({"error": error_msg}), 500

@app.route('/api/scrape_leads', methods=['POST'])
def scrape_global_leads():
    data = request.json or {}
    location = data.get('location', 'Miami')
    num_results = data.get('num_results', 15)
    
    try:
        leads = agent_scraper.scrape_leads(location, num_results=int(num_results))
        return jsonify({"leads": leads})
    except Exception as e:
        print(f"Scraping Error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("V2 Flask Dashboard running on http://localhost:8000")
    app.run(port=8000, debug=True)

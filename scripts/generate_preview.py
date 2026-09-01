import os
import sys
import json
import re
import shutil
import argparse
import urllib.request

# New Gemini Prompt based on the Knowledgebase for Yacht Charters
SYSTEM_PROMPT = """
You are a luxury branding specialist and full-stack designer for ultra-high-net-worth maritime businesses.

Task:
1. Identify 2 specific UX/conversion flaws on their current website (e.g., poor mobile fleet layout, slow loading images, lack of clear spec badges).
2. Generate an ultra-luxurious `siteConfig.json` following the yacht template schema, with elegant copywriting, refined fleet descriptions, and verified Unsplash marine photography.
3. Output strictly valid JSON matching the schema below.

Required Schema:
{
  "companyName": "Name of business",
  "baseLocation": "City or Region",
  "heroTitle": "High impact luxury headline for section 1",
  "heroSubtitle": "Compelling subheadline for section 1",
  "services": [
    {
      "title": "Service or Value Prop 1 for section 2",
      "desc": "Description for section 2"
    },
    {
      "title": "Service or Value Prop 2 for section 3",
      "desc": "Description for section 3"
    }
  ],
  "bookingCtaUrl": "https://cal.com/your-agency/yacht-consult"
}
"""

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def call_gemini_api(api_key, business_name, city, overview_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    
    user_prompt = f"""
    Target Prospect:
    Company Name: {business_name}
    Location: {city}
    Current Website / Listing Info: {overview_text}
    
    Please generate the customized `siteConfig.json` object.
    Output ONLY valid JSON inside markdown block ```json ... ``` or as plain JSON.
    """
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": SYSTEM_PROMPT},
                    {"text": user_prompt}
                ]
            }
        ],
        "generationConfig": {
            "response_mime_type": "application/json",
            "temperature": 0.7
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            text_response = res_data['candidates'][0]['content']['parts'][0]['text']
            return json.loads(text_response)
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return None

def generate_preview(business_name, city, overview_text, api_key=None):
    slug = slugify(business_name)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(base_dir, "previews", slug)
    
    os.makedirs(target_dir, exist_ok=True)
    
    config_data = None
    if api_key:
        print(f"Calling Gemini API to analyze {business_name}...")
        config_data = call_gemini_api(api_key, business_name, city, overview_text)
    
    if not config_data:
        print("Using base template config with populated parameters...")
        with open(os.path.join(base_dir, "siteConfig.json"), "r") as f:
            config_data = json.load(f)
        config_data["companyName"] = business_name
        config_data["baseLocation"] = city
    
    # Write siteConfig.json to client folder
    with open(os.path.join(target_dir, "siteConfig.json"), "w") as f:
        json.dump(config_data, f, indent=2)
        
    # Copy frontend assets to client folder
    for file_name in ["index.html", "style.css", "main.js"]:
        src = os.path.join(base_dir, file_name)
        if os.path.exists(src):
            # If it's index.html, update the video path to point to the root folder
            if file_name == "index.html":
                with open(src, "r") as html_file:
                    html_content = html_file.read()
                html_content = html_content.replace('src="./video_smooth.mp4"', 'src="../../video_smooth.mp4"')
                html_content = html_content.replace("src='video_smooth.mp4'", "src='../../video_smooth.mp4'")
                html_content = html_content.replace('src="video_smooth.mp4"', 'src="../../video_smooth.mp4"')
                with open(os.path.join(target_dir, file_name), "w") as html_dest:
                    html_dest.write(html_content)
            else:
                shutil.copy(src, os.path.join(target_dir, file_name))
    
    print(f"[SUCCESS] Preview generated successfully!")
    print(f"[PATH] Local Path: {target_dir}")
    print(f"[URL] GitHub Pages URL: https://elevateweb.me/client-previews/previews/{slug}/")
    
    return target_dir

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate client preview site")
    parser.add_argument("--name", required=True, help="Business Name")
    parser.add_argument("--city", default="Miami, FL", help="City, State")
    parser.add_argument("--overview", default="Outdated luxury charter site missing instant online booking.", help="Current website notes")
    parser.add_argument("--api-key", default=os.getenv("GEMINI_API_KEY"), help="Google AI Studio Gemini API Key")
    parser.add_argument("--auto-commit", action="store_true", help="Automatically commit and push to git")
    
    args = parser.parse_args()
    target_dir = generate_preview(args.name, args.city, args.overview, args.api_key)
    
    if args.auto_commit and target_dir:
        print(f"Auto-committing {target_dir} to git...")
        import subprocess
        try:
            subprocess.run(["git", "add", target_dir], check=True)
            subprocess.run(["git", "commit", "-m", f"Add auto-generated preview for {args.name}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Successfully pushed to GitHub!")
        except Exception as e:
            print(f"Error during git operations: {e}")

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
  "founderName": "Captain or Founder Name",
  "baseLocation": "City or Region",
  "phone": "Phone Number",
  "email": "contact email",
  "primaryColor": "#BBA992",
  "heroTitle": "High impact luxury headline",
  "heroSubtitle": "Compelling subheadline focusing on VIP experience.",
  "fleet": [
    {
      "name": "Vessel Name & Specs",
      "specs": "Guests • Cabins • Crew • Knots",
      "dayRate": "$XXX / day",
      "amenities": ["Feature 1", "Feature 2", "Feature 3"],
      "image": "https://images.unsplash.com/photo-XXX?auto=format&fit=crop&w=1200&q=80"
    }
  ],
  "destinations": [
    "Destination 1",
    "Destination 2",
    "Destination 3"
  ],
  "certifications": ["MYBA Certified", "Licensed Master Captains"],
  "bookingCtaUrl": "https://cal.com/your-agency/yacht-consult",
  "flawsFixed": ["Flaw 1 fix description", "Flaw 2 fix description"]
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
        
    # Copy index.html to client folder
    shutil.copy(os.path.join(base_dir, "index.html"), os.path.join(target_dir, "index.html"))
    
    # Copy assets if available
    assets_dir = os.path.join(base_dir, "assets")
    if os.path.exists(assets_dir):
        target_assets = os.path.join(target_dir, "assets")
        if os.path.exists(target_assets):
            shutil.rmtree(target_assets)
        shutil.copytree(assets_dir, target_assets)
    
    print(f"[SUCCESS] Preview generated successfully!")
    print(f"[PATH] Local Path: {target_dir}")
    print(f"[URL] GitHub Pages URL: https://elevateweb.me/client-previews/previews/{slug}/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate client preview site")
    parser.add_argument("--name", required=True, help="Business Name")
    parser.add_argument("--city", default="Miami, FL", help="City, State")
    parser.add_argument("--overview", default="Outdated luxury charter site missing instant online booking.", help="Current website notes")
    parser.add_argument("--api-key", default=os.getenv("GEMINI_API_KEY"), help="Google AI Studio Gemini API Key")
    
    args = parser.parse_args()
    generate_preview(args.name, args.city, args.overview, args.api_key)

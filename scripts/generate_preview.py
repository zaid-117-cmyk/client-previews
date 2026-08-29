import os
import sys
import json
import re
import shutil
import argparse
import urllib.request

# Default Gemini Prompt for Yacht / Boat Charter Niche
SYSTEM_PROMPT = """
You are a master conversion-rate-optimization (CRO) specialist and high-ticket copywriter for luxury hospitality and yacht charter businesses.
Analyze the provided business details and generate a JSON configuration for a modernized, high-converting website.

Output strictly valid JSON matching this schema:
{
  "businessName": "Name of business",
  "tagline": "Punchy luxury tagline",
  "city": "City, State",
  "phone": "(XXX) XXX-XXXX",
  "email": "contact email",
  "ctaBookingUrl": "https://cal.com/your-agency/10min",
  "hero": {
    "headline": "High impact luxury headline",
    "subheadline": "Compelling subheadline focusing on VIP experience and charter options.",
    "bgImage": "https://images.unsplash.com/photo-1569263979104-865ab7cd8d13?q=80&w=1920&auto=format&fit=crop",
    "badge": "★ #1 Rated Luxury Charter Service in [City]"
  },
  "stats": [
    {"label": "5-Star Reviews", "value": "200+"},
    {"label": "Private Fleet", "value": "6+ Vessels"},
    {"label": "Charter Hours", "value": "8,000+"},
    {"label": "Captain Experience", "value": "12+ Yrs"}
  ],
  "fleet": [
    {
      "name": "Vessel Name & Specs",
      "capacity": "XX Guests",
      "speed": "XX Knots",
      "price": "$XXX / hr",
      "image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?q=80&w=800&auto=format&fit=crop",
      "features": ["Feature 1", "Feature 2", "Feature 3", "Feature 4"]
    }
  ],
  "experiences": [
    {
      "title": "Experience Title",
      "duration": "Duration (e.g. 4 Hours)",
      "description": "Short alluring description"
    }
  ],
  "testimonials": [
    {
      "author": "Client Name",
      "role": "Charter Type",
      "review": "Enthusiastic review text"
    }
  ],
  "flawsFixed": [
    "Flaw 1 fix description",
    "Flaw 2 fix description",
    "Flaw 3 fix description"
  ]
}
"""

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def call_gemini_api(api_key, business_name, city, overview_text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro:generateContent?key={api_key}"
    
    user_prompt = f"""
    Business Name: {business_name}
    City/Location: {city}
    Current Website / Overview Text: {overview_text}
    
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
        config_data["businessName"] = business_name
        config_data["city"] = city
    
    # Write siteConfig.json to client folder
    with open(os.path.join(target_dir, "siteConfig.json"), "w") as f:
        json.dump(config_data, f, indent=2)
        
    # Copy index.html to client folder
    shutil.copy(os.path.join(base_dir, "index.html"), os.path.join(target_dir, "index.html"))
    
    print(f"[SUCCESS] Preview generated successfully!")
    print(f"[PATH] Local Path: {target_dir}")
    print(f"[URL] GitHub Pages URL: https://<username>.github.io/client-previews/previews/{slug}/")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate client preview site")
    parser.add_argument("--name", required=True, help="Business Name")
    parser.add_argument("--city", default="Miami, FL", help="City, State")
    parser.add_argument("--overview", default="Outdated luxury charter site missing instant online booking.", help="Current website notes")
    parser.add_argument("--api-key", default=os.getenv("GEMINI_API_KEY"), help="Google AI Studio Gemini API Key")
    
    args = parser.parse_args()
    generate_preview(args.name, args.city, args.overview, args.api_key)

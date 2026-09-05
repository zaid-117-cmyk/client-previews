import os
import sys
import json
import re
import shutil
import argparse
import urllib.request

# New Gemini Prompt based on the Knowledgebase for Yacht Charters
SYSTEM_PROMPT_YACHT = """
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

SYSTEM_PROMPT_REAL_ESTATE = """
You are a luxury real estate branding specialist.

Task:
1. Identify 2 specific conversion flaws on their current real estate website (e.g., poor property listings, lack of trust badges).
2. Generate an ultra-luxurious `siteConfig.json` following the real estate template schema.
3. Output strictly valid JSON matching the schema below.

Required Schema:
{
  "companyName": "Name of real estate agency or broker",
  "baseLocation": "City or Region (e.g., Beverly Hills, CA)",
  "heroTitle": "High impact luxury headline",
  "heroSubtitle": "Compelling subheadline",
  "services": [
    {
      "title": "Property Name or Address",
      "desc": "Beds, Baths | Short description - $Price"
    },
    {
      "title": "Property 2 Name or Address",
      "desc": "Beds, Baths | Short description - $Price"
    }
  ],
  "bookingCtaUrl": "https://cal.com/your-agency/estate-consult"
}
"""

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def call_gemini_api(api_key, business_name, city, overview_text, niche="yacht"):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.6-flash:generateContent?key={api_key}"
    sys_prompt = SYSTEM_PROMPT_YACHT if niche == "yacht" else SYSTEM_PROMPT_REAL_ESTATE
    
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
                    {"text": sys_prompt},
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
            
            # Strip markdown if present
            if text_response.strip().startswith("```json"):
                text_response = text_response.strip().removeprefix("```json").removesuffix("```").strip()
            elif text_response.strip().startswith("```"):
                text_response = text_response.strip().removeprefix("```").removesuffix("```").strip()
                
            return json.loads(text_response)
    except Exception as e:
        error_msg = str(e)
        if hasattr(e, 'read'):
            try:
                error_msg = e.read().decode('utf-8')
            except:
                pass
        print(f"Error calling Gemini API: {error_msg}")
        return None

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

def generate_preview(business_name, city, overview_text, api_key=None, niche="yacht"):
    slug = slugify(business_name)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(base_dir, "previews", slug)
    
    os.makedirs(target_dir, exist_ok=True)
    
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
        
    config_data = None
    if api_key:
        print(f"Calling Gemini API (gemini-3.6-flash) to analyze {business_name}...")
        config_data = call_gemini_api(api_key, business_name, city, overview_text, niche=niche)
    
    template_dir = "yacht_template" if not niche or niche == "yacht" else "real_estate_template"
    
    if not config_data:
        print(f"Using base template config for {template_dir}...")
        with open(os.path.join(base_dir, template_dir, "siteConfig.json"), "r") as f:
            config_data = json.load(f)
        config_data["companyName"] = business_name
        config_data["baseLocation"] = city
    
    # Write siteConfig.json to client folder
    with open(os.path.join(target_dir, "siteConfig.json"), "w") as f:
        json.dump(config_data, f, indent=2)
        
    # Copy frontend files to client folder
    for file_name in ["index.html", "style.css", "main.js"]:
        src = os.path.join(base_dir, template_dir, file_name)
        if os.path.exists(src):
            shutil.copy(src, os.path.join(target_dir, file_name))
            
    # Copy assets folder to client folder so the video works natively!
    assets_src = os.path.join(base_dir, "assets")
    assets_dest = os.path.join(target_dir, "assets")
    if os.path.exists(assets_src):
        if os.path.exists(assets_dest):
            shutil.rmtree(assets_dest)
        shutil.copytree(assets_src, assets_dest)
    
    print(f"[SUCCESS] Preview generated successfully!")
    print(f"[PATH] Local Path: {target_dir}")
    print(f"[URL] GitHub Pages URL: https://elevateweb.me/client-previews/previews/{slug}/")
    
    return target_dir

def manual_gemini_workflow(business_name, city, overview_text, niche="yacht"):
    sys_prompt = SYSTEM_PROMPT_YACHT if niche == "yacht" else SYSTEM_PROMPT_REAL_ESTATE
    user_prompt = f"""
Target Prospect:
Company Name: {business_name}
Location: {city}
Current Website / Listing Info: {overview_text}

Please generate the customized `siteConfig.json` object.
Output ONLY valid JSON inside markdown block ```json ... ``` or as plain JSON.
"""
    print("\n" + "="*60)
    print("   MANUAL GEMINI MODE   ")
    print("="*60)
    print("\nSTEP 1: Copy the entire text below (between the lines) and paste it into gemini.google.com:\n")
    print("-" * 60)
    print(sys_prompt.strip())
    print(user_prompt.strip())
    print("-" * 60)
    
    print("\nSTEP 2: Once Gemini generates the JSON, paste it below.")
    print("Type 'EOF' on a new line and press Enter when you are done pasting:\n")
    
    lines = []
    while True:
        try:
            line = input()
            if line.strip() == "EOF":
                break
            lines.append(line)
        except EOFError:
            break
            
    text_response = "\n".join(lines)
    
    # Strip markdown if present
    if text_response.strip().startswith("```json"):
        text_response = text_response.strip().removeprefix("```json").removesuffix("```").strip()
    elif text_response.strip().startswith("```"):
        text_response = text_response.strip().removeprefix("```").removesuffix("```").strip()
        
    try:
        config_data = json.loads(text_response)
        return config_data
    except Exception as e:
        print(f"\n[!] Failed to parse JSON. Did you paste exactly what Gemini outputted? Error: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate client preview site")
    parser.add_argument("--name", required=True, help="Business Name")
    parser.add_argument("--city", default="Miami, FL", help="City, State")
    parser.add_argument("--overview", default="Outdated luxury charter site missing instant online booking.", help="Current website notes")
    parser.add_argument("--api-key", default=os.getenv("GEMINI_API_KEY"), help="Google AI Studio Gemini API Key")
    parser.add_argument("--manual", action="store_true", help="Use manual copy-paste workflow to avoid API limits")
    parser.add_argument("--auto-commit", action="store_true", help="Automatically commit and push to git")
    parser.add_argument("--niche", default="yacht", choices=["yacht", "real_estate"], help="Target niche for template routing")
    
    args = parser.parse_args()
    
    if args.manual:
        config_data = manual_gemini_workflow(args.name, args.city, args.overview, args.niche)
        if config_data:
            template_dir = "yacht_template" if args.niche == "yacht" else "real_estate_template"
            # We bypass the API call inside generate_preview by setting api_key=None 
            # and modifying the template manually here, or we can just pass the config_data 
            # into a slightly modified generate_preview. Let's just write a quick inline override.
            slug = slugify(args.name)
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            target_dir = os.path.join(base_dir, "previews", slug)
            os.makedirs(target_dir, exist_ok=True)
            
            with open(os.path.join(target_dir, "siteConfig.json"), "w") as f:
                json.dump(config_data, f, indent=2)
                
            for file_name in ["index.html", "style.css", "main.js"]:
                src = os.path.join(base_dir, template_dir, file_name)
                if os.path.exists(src):
                    shutil.copy(src, os.path.join(target_dir, file_name))
            
            assets_src = os.path.join(base_dir, "assets")
            assets_dest = os.path.join(target_dir, "assets")
            if os.path.exists(assets_src):
                if os.path.exists(assets_dest):
                    shutil.rmtree(assets_dest)
                shutil.copytree(assets_src, assets_dest)
                
            print(f"\n[SUCCESS] Manual Preview generated successfully!")
            print(f"[PATH] Local Path: {target_dir}")
            target_dir_result = target_dir
        else:
            print("Aborting generation due to JSON error.")
            sys.exit(1)
    else:
        target_dir_result = generate_preview(args.name, args.city, args.overview, args.api_key, args.niche)
    
    
    if args.auto_commit and target_dir_result:
        print(f"Auto-committing {target_dir_result} to git...")
        import subprocess
        try:
            subprocess.run(["git", "add", target_dir_result], check=True)
            subprocess.run(["git", "commit", "-m", f"Add auto-generated preview for {args.name}"], check=True)
            subprocess.run(["git", "push"], check=True)
            print("Successfully pushed to GitHub!")
        except Exception as e:
            print(f"Error during git operations: {e}")

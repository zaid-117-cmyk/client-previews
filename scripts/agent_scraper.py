import os
import csv
import re
import time
import requests
from bs4 import BeautifulSoup

try:
    from googlesearch import search
except ImportError:
    print("Please install the required package: pip install googlesearch-python beautifulsoup4")
    exit(1)

def extract_emails_from_url(url):
    """Visits a URL and extracts any email addresses found on the page."""
    try:
        # Use a realistic User-Agent to avoid getting blocked
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        
        # Only parse if the request was successful
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            
            # Simple Regex for extracting emails
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = set(re.findall(email_pattern, text))
            
            # Filter out common junk emails (like wix@, sentry@, etc)
            valid_emails = [e for e in emails if not e.startswith('sentry') and not e.endswith('.png')]
            return valid_emails
    except Exception as e:
        print(f"  [!] Failed to scrape {url}: {e}")
    
    return []

def scrape_leads(location, num_results=10):
    query = f"Yacht Charter {location}"
    print(f"\n[START] Agent 1 Starting: Searching for '{query}'...")
    
    leads = []
    
    # Search Google for the query
    try:
        urls = list(search(query, num_results=num_results, sleep_interval=2))
    except Exception as e:
        print(f"Error querying Google: {e}")
        return
        
    print(f"Found {len(urls)} websites. Extracting emails...")
    
    for url in urls:
        print(f"-> Scanning {url}...")
        emails = extract_emails_from_url(url)
        
        if emails:
            for email in emails:
                print(f"   [+] Found Email: {email}")
                # We try to extract a pseudo-company name from the URL
                domain = url.split("//")[-1].split("/")[0].replace("www.", "")
                company_name = domain.split(".")[0].capitalize()
                
                leads.append({
                    "First Name": "Owner",
                    "Company": company_name,
                    "Email": email.lower(),
                    "Website": url
                })
        else:
            print("   [-] No emails found.")
            
        # Polite delay to avoid IP bans
        time.sleep(2)
        
    # Remove duplicates
    unique_leads = {lead["Email"]: lead for lead in leads}.values()
    
    # Save to CSV
    output_file = f"leads_scraped_{location.replace(' ', '_').lower()}.csv"
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["First Name", "Company", "Email", "Website"])
        writer.writeheader()
        writer.writerows(unique_leads)
        
    print(f"\n[SUCCESS] Scraping Complete! Saved {len(unique_leads)} unique leads to {output_file}")
    print(f"You can now copy these into your main leads.csv file for the outreach campaign.")
    
    return list(unique_leads)

if __name__ == "__main__":
    # You can change the location here to target different hotspots!
    target_location = input("Enter a city to scrape (e.g., Monaco, Dubai, Miami): ")
    scrape_leads(target_location, num_results=15)

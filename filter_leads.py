import os
import csv
import json
import sys

base_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(base_dir, "dashboard", "data", "campaign_log.json")
csv_out = os.path.join(base_dir, "leads.csv")

# Allow passing input CSV as argument, or fallback to common local locations
if len(sys.argv) > 1:
    csv_in = sys.argv[1]
elif os.path.exists(os.path.join(base_dir, "leads_raw.csv")):
    csv_in = os.path.join(base_dir, "leads_raw.csv")
elif os.path.exists(r"D:\EDGE DOWNLOADS\leads3.csv"):
    csv_in = r"D:\EDGE DOWNLOADS\leads3.csv"
else:
    csv_in = os.path.join(base_dir, "leads_scraped_miami.csv")

if not os.path.exists(csv_in):
    print(f"Error: Input leads file not found: {csv_in}")
    print("Usage: python filter_leads.py <path_to_apollo_or_scraped_leads.csv>")
    sys.exit(1)

contacted = set()
if os.path.exists(log_path):
    with open(log_path, 'r', encoding='utf-8') as f:
        logs = json.load(f)
        for log in logs:
            if "email" in log:
                contacted.add(log["email"].strip().lower())

new_leads = []
duplicates_removed = 0
total_processed = 0

with open(csv_in, 'r', encoding='utf-8-sig') as f:
    reader = csv.reader(f)
    header = next(reader)
    new_leads.append(header)
    
    # Try to find email column index
    email_idx = -1
    for i, col in enumerate(header):
        if col.strip().lower() == "email":
            email_idx = i
            break
            
    if email_idx == -1:
        print("Error: Could not find 'email' column in CSV header.")
        exit(1)
        
    for row in reader:
        if not row:
            continue
        total_processed += 1
        if len(row) > email_idx:
            email = row[email_idx].strip().lower()
            if email and email not in contacted:
                new_leads.append(row)
            else:
                duplicates_removed += 1
            
with open(csv_out, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerows(new_leads)
    
print(f"Filter Complete!")
print(f"Total leads checked: {total_processed}")
print(f"Already contacted (removed): {duplicates_removed}")
print(f"Clean leads to email: {len(new_leads) - 1}")

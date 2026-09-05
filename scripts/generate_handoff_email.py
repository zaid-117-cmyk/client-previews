import os
import argparse
try:
    import google.generativeai as genai
except ImportError:
    print("Please install google-generativeai: pip install google-generativeai")
    exit(1)

def generate_handoff_email(client_name, company_name):
    print(f"Generating white-glove handoff email for {client_name}...\n")
    
    email_body = f"""
Dear {client_name},

I am thrilled to inform you that the custom luxury website for {company_name} is fully complete and ready for deployment.

As promised, to ensure you have 100% ownership and zero ongoing monthly hosting fees, we have packaged the entire digital asset into a secure ZIP file, which is attached to this email.

To deploy your site globally, simply follow these two steps:
1. Create a free account at Netlify.com
2. Drag and drop the attached ZIP file into their deployment box

Your site will be live instantly on a high-speed CDN.

Congratulations on your new digital asset. If you need any assistance during the drag-and-drop process, please let me know.

Best regards,
Director of Design
"""
    
    print("=====================================================")
    print("SUBJECT: Your New Digital Asset is Ready for Deployment")
    print("=====================================================\n")
    print(email_body.strip())
    print("\n=====================================================")
    print("Action: Attach the ZIP file you manually created and send!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a white-glove handoff email using Gemini.")
    parser.add_argument("--name", type=str, required=True, help="The client's first name")
    parser.add_argument("--company", type=str, required=True, help="The client's company name")
    
    args = parser.parse_args()
    generate_handoff_email(args.name, args.company)

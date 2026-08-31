# Setting Up the GitHub Student Developer Pack

This guide explains how to connect the free tools from the GitHub Student Developer Pack to this AI-powered outreach system, ensuring your running costs remain at $0.

## 1. Claiming Your Free Domain
Through the Student Pack, you get a free `.me` (from Namecheap) or `.tech` / `.live` (from Name.com) domain for 1 year.

1. Go to the [GitHub Student Developer Pack](https://education.github.com/pack).
2. Scroll to Namecheap or Name.com and click to claim your free domain.
3. Choose a professional agency name (e.g., `elevateweb.me`).

## 2. Setting Up Cloudflare (Free Tier)
We will route your new domain through Cloudflare for free DNS management, SSL, and Email Routing.

1. Create a free account at [Cloudflare](https://dash.cloudflare.com/sign-up).
2. Click **Add Site** and enter your new `.me` domain.
3. Select the **Free plan**.
4. Cloudflare will give you two Nameservers (e.g., `dave.ns.cloudflare.com`). 
5. Go back to Namecheap/Name.com, find your domain settings, and change the **Nameservers** to the ones Cloudflare provided.

## 3. GitHub Pages Hosting (CI/CD Pipeline)
Your generated prospect sites are hosted completely free on GitHub Pages.

1. Create a new public repository (e.g., `ai-website-outreach`).
2. Push this codebase to the `main` branch.
3. Go to **Settings > Pages**.
4. Under **Build and deployment**, select **GitHub Actions** as the source.
5. Optional: Under **Custom domain**, enter your new `.me` domain (e.g., `previews.elevateweb.me`). Cloudflare will automatically secure this with SSL.

*(Our `.github/workflows/deploy.yml` will automatically build and publish any new client folders you add!)*

## 4. Free Email Delivery setup (SMTP)
You need to send emails to prospects.

### Option A: Cloudflare Email Routing + Gmail (Easiest & Free)
1. In Cloudflare, go to **Email Routing**.
2. Create a custom address (e.g., `hello@elevateweb.me`) and forward it to your personal Gmail.
3. Add Cloudflare's required TXT records to your DNS (Cloudflare does this automatically with one click).
4. Set up an App Password in your Google Account settings. Use your Gmail credentials in the `auto_responder.py` environment variables.

### Option B: SendGrid (Free Tier)
1. Claim the SendGrid student offer for 15,000 free emails/month.
2. Authenticate your domain by adding SendGrid's CNAME records to Cloudflare DNS.
3. Generate an API Key to use as the password in your `auto_responder.py` script.

## 5. Hosting the Auto-Responder (DigitalOcean)
You get $200 in free DigitalOcean credits via the Student Pack. You can use this to keep the `auto_responder.py` script running 24/7 so it can instantly reply to prospects.

1. Claim the DigitalOcean credit from the Student Pack dashboard.
2. Create a basic $4/month Droplet (Ubuntu).
3. SSH into the Droplet, clone this repository, and run the script inside a `tmux` or `screen` session.
4. Set your environment variables (`EMAIL_USER`, `EMAIL_PASS`, `GEMINI_API_KEY`) on the server.

---
**You are now fully set up with a $0/month automated outreach machine!**

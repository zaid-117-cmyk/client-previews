# Email Deliverability & DNS Setup Guide

If you send cold emails without setting up SPF, DKIM, and DMARC, your emails will land in the spam folder 100% of the time. 

Follow this guide to securely configure `elevateweb.me` via Cloudflare so you get a 10/10 inbox rate.

## Step 1: Connect your Domain to Cloudflare
1. Create a free account at [Cloudflare](https://dash.cloudflare.com).
2. Click **Add a Site** and enter `elevateweb.me`.
3. Select the **Free** plan.
4. Cloudflare will scan your current DNS records. Click **Continue**.
5. Cloudflare will give you two "Nameservers" (e.g., `amy.ns.cloudflare.com` and `bob.ns.cloudflare.com`).
6. Log into your GitHub Student Developer Pack provider (Namecheap/Name.com) where you got `elevateweb.me`.
7. Find the "Nameservers" section and select "Custom DNS". Paste the two Cloudflare nameservers there.
8. Wait ~15 minutes and click "Check nameservers" in Cloudflare.

## Step 2: Set up Cloudflare Email Routing (Free)
This allows you to create `hello@elevateweb.me` and have it forward to your personal Gmail.
1. In your Cloudflare Dashboard for `elevateweb.me`, click **Email** -> **Email Routing** on the left menu.
2. Click **Get Started**.
3. Under **Custom Address**, type `hello` (so it becomes `hello@elevateweb.me`).
4. Under **Destination Address**, enter your personal Gmail address.
5. Cloudflare will send a verification email to your Gmail. Open it and click Verify.
6. Cloudflare will now ask to automatically add the required MX and SPF records to your DNS. Click **Add records automatically**.

## Step 3: Configure "Send As" in Gmail
Now that you can receive emails at `hello@elevateweb.me`, you need to be able to *send* from it.
1. Go to your Gmail settings (the gear icon) -> **See all settings**.
2. Click on the **Accounts and Import** tab.
3. Under "Send mail as", click **Add another email address**.
4. Name: Your Name | Email address: `hello@elevateweb.me`.
5. Uncheck "Treat as an alias" and click Next Step.
6. **SMTP Server Details:**
   - SMTP Server: `smtp.gmail.com`
   - Port: `465`
   - Username: *Your personal Gmail address*
   - Password: *The 16-letter App Password you generated earlier*
7. Click **Add Account**. 
8. You can now select `hello@elevateweb.me` from the "From" dropdown whenever you compose an email!

## Step 4: Add DKIM and DMARC (The Anti-Spam Shield)
Finally, add these to your Cloudflare DNS tab to prove you aren't a spammer.
1. Go to **DNS** -> **Records** in Cloudflare.
2. Click **Add record**.
3. **DKIM Record:** (Since we are using Gmail to send)
   - Type: `TXT`
   - Name: `google._domainkey`
   - Content: *(You will need to generate this from Google Workspace if you have it, otherwise skip DKIM and rely on SPF/DMARC)*
4. **DMARC Record:**
   - Type: `TXT`
   - Name: `_dmarc`
   - Content: `v=DMARC1; p=none; rua=mailto:hello@elevateweb.me`

## Step 5: Test Your Deliverability
Before sending to any Yacht Charters, go to [Mail-Tester.com](https://www.mail-tester.com/).
1. Copy the random email address they give you on the screen.
2. Go to your Gmail, select `hello@elevateweb.me` as the sender, and send a test email to that random address.
3. Click "Then check your score". Aim for a **10/10**.

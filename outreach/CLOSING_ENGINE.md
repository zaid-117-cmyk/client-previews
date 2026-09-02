# The Closing Engine (Razorpay Edition)

Now that the AI is generating leads and building websites for you, your only job is to jump on a quick 15-minute call and collect the cash. 

Here is your complete system for closing the deal.

---

## 1. The Razorpay Setup

Since you are using Razorpay instead of Stripe, the easiest way to collect high-ticket payments instantly on a Zoom call is to use **Razorpay Payment Links**.

**How to set it up:**
1. Log in to your Razorpay Dashboard.
2. Go to **Payment Links** on the left menu and click **Create Payment Link**.
3. **Amount:** Set this to your upfront build fee (e.g., $1,000 or ₹80,000).
4. **Description:** "Custom Website Build & Optimization for [Client Name]"
5. Keep the link open in a tab during your sales call. As soon as they agree to buy, you simply drop this link in the Zoom chat or email it to them so they can pay instantly via UPI, Credit Card, or Netbanking.

*If you want to charge a monthly retainer (e.g., $100/mo for hosting/maintenance), you can set up a **Razorpay Subscription** instead.*

---

## 2. The 15-Minute Zoom Sales Script

When the client clicks the link in your automated email and books a call with you, they have already seen the prototype. *They are already 90% sold.* Your job is not to sell; it is to confirm.

**Step 1: The Opener (2 mins)**
> "Hey [Name], great to meet you! I'm glad you liked the prototype I sent over. I know you're super busy running the charters, so I'll keep this brief. I mainly just wanted to walk you through the new site and see what you thought."

**Step 2: The Walkthrough (5 mins)**
*Share your screen and pull up the AI-generated preview link.*
> "As you can see, I completely overhauled the mobile booking flow. Most of your high-end clients are booking from their iPhones, so I made sure the 'Inquire Now' button is sticky and always visible. I also added that drone video we pulled in to give it that premium feel. Are there any specific photos or text you'd want swapped out if we made this your official site?"
*(Listen to their feedback and say yes to their small tweaks).*

**Step 3: The Pitch & Price (3 mins)**
> "Awesome. So normally, agencies charge $5,000+ for a custom setup like this and take 2 months to build it. Because I've already built the entire foundation for you, I can literally have this fully live on your actual domain by tomorrow. My fee is just a one-time payment of $1,000 for the build, and then $100 a month to cover the premium hosting, security, and any minor text changes you need throughout the year. How does that sound?"

**Step 4: The Close (2 mins)**
> "Perfect. Let's get this live for you. I'm going to drop a Razorpay link in the Zoom chat right now for the $1,000 build fee. Once that's processed, I'll need you to log into your GoDaddy/Namecheap account so we can point your domain to the new site, and we are officially in business!"

---

## 3. Post-Payment Fulfillment (Technical Step)

Once they pay the Razorpay link, you need to deliver the website. Because it's already hosted on your GitHub Pages, delivering it is incredibly easy:

1. Ask the client where they bought their domain (GoDaddy, Namecheap, etc.).
2. Ask them to add you as a "Delegate" or "Collaborator" on their domain account.
3. You will log in, go to their DNS settings, and point their `A Records` to GitHub's servers (exactly like you did for `elevateweb.me`).
4. Go to your GitHub repository -> Settings -> Pages -> Custom Domain, and type in their domain name.
5. The AI-generated site is now officially their live website!

*(If they need completely different features like a complex backend database later, you can easily migrate the HTML/CSS the AI built into WordPress or Webflow).*

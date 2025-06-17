# Email Setup Guide

## MindMirror Email Capture & Welcome Emails

This setup uses **Resend** for transactional emails and **React Email** for beautiful email templates.

### 1. Get Your Resend API Key

1. Go to [resend.com](https://resend.com)
2. Sign up for a free account (100 emails/day free)
3. Navigate to [API Keys](https://resend.com/api-keys)
4. Create a new API key
5. Copy the key (starts with `re_`)

### 2. Add Environment Variable

Create a `.env.local` file in your `/web` directory:

```bash
RESEND_API_KEY=re_your_actual_api_key_here
```

### 3. Domain Setup (Optional for Production)

For production, you'll want to:

1. Add your domain in Resend dashboard
2. Verify DNS records
3. Update the `from` email in `/src/app/api/subscribe/route.ts`

### 4. Test the Email Flow

1. Start your dev server: `npm run dev`
2. Go to `/landing`
3. Enter your email in the signup form
4. Check your email for the welcome message!

### 5. Email Template

The welcome email template is in `/emails/welcome-email.tsx` and includes:

- 🧠 MindMirror branding
- Beautiful React Email design
- Early access messaging
- Swae OS integration
- Call-to-action buttons

### 6. Database Integration (TODO)

Currently, emails are just logged to console. For production, you'll want to:

- Add a database (PostgreSQL, MongoDB, etc.)
- Store subscriber emails with timestamps
- Track email engagement
- Build an admin dashboard

### 7. Analytics & Tracking

Consider adding:

- Email open tracking
- Click tracking on CTAs
- Conversion funnel analysis
- A/B testing for email content

---

🎉 **You're all set!** The landing page now captures emails and sends beautiful welcome messages automatically. 
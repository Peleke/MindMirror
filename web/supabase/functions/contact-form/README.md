# Contact Form Edge Function

A production-ready Supabase Edge function for handling contact form submissions with email delivery via Resend.

## Features

- ✅ TypeScript with full type safety
- ✅ Input validation and sanitization  
- ✅ Email format validation
- ✅ CORS support
- ✅ Error handling and logging
- ✅ Rate limiting friendly
- ✅ Clean HTML email templates
- ✅ Multi-source form support

## Environment Variables

Set these in your Supabase project:

```bash
# Resend API key (get from https://resend.com)
RESEND_API_KEY=re_xxxxxxxxx

# Email address to receive contact form submissions
CONTACT_EMAIL=contact@yourdomain.com
```

## Deployment

1. **Deploy the function:**
   ```bash
   supabase functions deploy contact-form
   ```

2. **Set environment variables:**
   ```bash
   supabase secrets set RESEND_API_KEY=your_resend_api_key
   supabase secrets set CONTACT_EMAIL=your_contact_email
   ```

3. **Test the function:**
   ```bash
   curl -X POST 'https://your-project.supabase.co/functions/v1/contact-form' \
     -H 'Authorization: Bearer YOUR_ANON_KEY' \
     -H 'Content-Type: application/json' \
     -d '{
       "name": "Test User",
       "email": "test@example.com", 
       "message": "This is a test message",
       "source": "Test"
     }'
   ```

## Usage

### Frontend Integration

```typescript
const handleSubmit = async (formData: {
  name: string;
  email: string;
  message: string;
  source?: string;
}) => {
  try {
    const response = await fetch('/api/contact-form', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(formData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error);
    }

    const result = await response.json();
    console.log('Success:', result.message);
  } catch (error) {
    console.error('Error:', error.message);
  }
};
```

### API Endpoint

- **URL:** `https://your-project.supabase.co/functions/v1/contact-form`
- **Method:** POST
- **Headers:** 
  - `Content-Type: application/json`
  - `Authorization: Bearer YOUR_ANON_KEY` (optional for public access)

### Request Body

```json
{
  "name": "John Doe",
  "email": "john@example.com", 
  "message": "Hello, I'm interested in your product...",
  "source": "Landing Page" // optional
}
```

### Response

**Success (200):**
```json
{
  "success": true,
  "message": "Contact form submitted successfully",
  "emailId": "resend_email_id"
}
```

**Error (4xx/5xx):**
```json
{
  "error": "Error message description"
}
```

## Email Template

The function sends a clean HTML email with:
- Contact person's name and email
- Message content (with preserved formatting)
- Source identification
- Timestamp
- Professional styling

## Security Features

- Input sanitization (removes HTML tags)
- Email format validation
- Field length limits (name/email: 100 chars, message: 5000 chars)
- CORS protection
- Environment variable validation
- Error logging without exposing sensitive data

## Customization

To customize the email template, edit the `createEmailTemplate` function in `index.ts`. You can:
- Change the styling
- Add more fields
- Modify the layout
- Add your branding

## Troubleshooting

1. **"Server configuration error"** - Check environment variables are set
2. **"Invalid email format"** - Verify email validation logic
3. **"Failed to send email"** - Check Resend API key and domain setup
4. **CORS errors** - Verify the corsHeaders configuration matches your domain 
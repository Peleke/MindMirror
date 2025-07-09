# Drip Email Function Setup

This Supabase Edge Function sends automated drip emails to waitlist subscribers using Resend.

## 🚀 Deployment Steps

### 1. Set Environment Variables
```bash
# Set Resend API key
supabase secrets set RESEND_API_KEY=your_resend_api_key_here

# Set Supabase keys (if not already set)
supabase secrets set SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### 2. Deploy Function
```bash
# From the web directory
supabase functions deploy send_drip_emails
```

### 3. Schedule Daily Trigger
1. Go to Supabase Dashboard > Database > Scheduled Triggers
2. Create new trigger:
   - **Name**: `daily_drip_emails`
   - **Schedule**: `0 10 * * *` (10 AM UTC daily)
   - **Function**: `send_drip_emails`
   - **HTTP Method**: `POST`

## 📧 Email Sequence
- **Day 0**: Welcome email
- **Day 1**: Gentle thought about kindness
- **Day 2**: Healing is nonlinear
- **Day 3**: Reflection prompt
- **Day 4**: Growth is quiet
- **Day 5**: You're doing better than you think
- **Day 6**: End of week perspective
- **Day 14**: Re-engagement email

## 🔧 Configuration
- **From Email**: `mirror@mindmirror.app`
- **Max Drip Days**: 7 (stops after day 6)
- **Re-engagement**: Day 14

## 🧪 Testing
```bash
# Test function locally
supabase functions serve send_drip_emails

# Test with curl
curl -X POST http://localhost:54321/functions/v1/send_drip_emails
```

## 📊 Monitoring
Check Supabase Dashboard > Functions > Logs for execution results and errors. 
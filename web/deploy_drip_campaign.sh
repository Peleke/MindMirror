#!/bin/bash

# MindMirror Drip Campaign Deployment Script
# Run this from the web directory

set -e

echo "🚀 Deploying MindMirror Drip Campaign..."

# Check if we're in the right directory
if [ ! -f "supabase/functions/send_drip_emails/index.ts" ]; then
    echo "❌ Error: Please run this script from the web directory"
    exit 1
fi

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Error: Supabase CLI not found. Please install it first."
    echo "Visit: https://supabase.com/docs/guides/cli"
    exit 1
fi

echo "📧 Deploying drip email function..."
supabase functions deploy send_drip_emails

echo "✅ Function deployed successfully!"
echo ""
echo "🔧 Next steps:"
echo "1. Set your Resend API key:"
echo "   supabase secrets set RESEND_API_KEY=your_key_here"
echo ""
echo "2. Create a scheduled trigger in Supabase Dashboard:"
echo "   - Go to Database > Scheduled Triggers"
echo "   - Create trigger: daily_drip_emails"
echo "   - Schedule: 0 10 * * * (10 AM UTC daily)"
echo "   - Function: send_drip_emails"
echo ""
echo "3. Run the migration SQL if you have existing subscribers:"
echo "   - Execute web/sql/002_drip_campaign_migration.sql"
echo ""
echo "🎉 Your drip campaign is ready to go!" 
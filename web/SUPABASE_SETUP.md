# Supabase Setup Guide

## 1. Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note down your project URL and anon key from Settings > API

## 2. Environment Variables

Add these to your `.env.local` file:

```bash
# Resend API Key (existing)
RESEND_API_KEY=re_your_resend_key_here

# Supabase Configuration (NEW)
NEXT_PUBLIC_SUPABASE_URL=https://gaitofyakycvpwqfoevq.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=anon-key
SUPABASE_SERVICE_ROLE_KEY=role-key

# Admin Configuration (NEW)
ADMIN_EMAIL=your@email.com
ADMIN_PASSWORD=password

# App Configuration (NEW)
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

## 3. Database Schema

Run this SQL in your Supabase SQL Editor:

```sql
-- Create the waitlist schema
CREATE SCHEMA IF NOT EXISTS waitlist;

-- Grant usage on schema to authenticated users
GRANT USAGE ON SCHEMA waitlist TO authenticated;
GRANT USAGE ON SCHEMA waitlist TO service_role;

-- subscribers table (waitlist)
CREATE TABLE waitlist.subscribers (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  source VARCHAR(50) DEFAULT 'landing_page',
  status VARCHAR(20) DEFAULT 'active',
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL
);

-- email_events table (engagement tracking)
CREATE TABLE waitlist.email_events (
  id BIGSERIAL PRIMARY KEY,
  subscriber_id BIGINT REFERENCES waitlist.subscribers(id) ON DELETE CASCADE,
  email_id VARCHAR(255),
  event_type VARCHAR(50),
  event_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- admin_users table (separate from regular users)
CREATE TABLE waitlist.admin_users (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  role VARCHAR(50) DEFAULT 'admin',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Grant permissions on tables
GRANT ALL ON waitlist.subscribers TO service_role;
GRANT ALL ON waitlist.email_events TO service_role;
GRANT ALL ON waitlist.admin_users TO service_role;

-- Grant permissions on sequences
GRANT ALL ON SEQUENCE waitlist.subscribers_id_seq TO service_role;
GRANT ALL ON SEQUENCE waitlist.email_events_id_seq TO service_role;
GRANT ALL ON SEQUENCE waitlist.admin_users_id_seq TO service_role;

-- Enable Row Level Security
ALTER TABLE waitlist.subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE waitlist.email_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE waitlist.admin_users ENABLE ROW LEVEL SECURITY;

-- Admin-only access policies
CREATE POLICY "Admins can view all subscribers" ON waitlist.subscribers
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM waitlist.admin_users 
      WHERE admin_users.user_id = auth.uid()
    )
  );

CREATE POLICY "Admins can view all email events" ON waitlist.email_events
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM waitlist.admin_users 
      WHERE admin_users.user_id = auth.uid()
    )
  );

CREATE POLICY "Admins can manage admin users" ON waitlist.admin_users
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM waitlist.admin_users 
      WHERE admin_users.user_id = auth.uid()
    )
  );
```

## 4. Create First Admin User

After setting up the database, run this API call to create your first admin:

```bash
curl -X POST http://localhost:3001/api/admin/setup \
  -H "Content-Type: application/json" \
  -d '{"email": "peleke.s@protonmail.com", "password": "password"}'
```

## 5. Test the Setup

1. Visit `http://localhost:3000/admin/login`
2. Login with your admin credentials
3. You should be redirected to the admin dashboard

## Next Steps

After setup is complete:
- [ ] Update subscriber API to use Supabase
- [ ] Build admin dashboard
- [ ] Add webhook handling for email events
- [ ] Test full email capture flow 
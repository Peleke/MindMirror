-- MindMirror Waitlist Database Setup
-- Run this in your Supabase SQL Editor

-- Create the waitlist schema
CREATE SCHEMA IF NOT EXISTS waitlist;

-- Grant usage on schema to authenticated users and service role
GRANT USAGE ON SCHEMA waitlist TO authenticated;
GRANT USAGE ON SCHEMA waitlist TO service_role;

-- subscribers table (waitlist)
CREATE TABLE IF NOT EXISTS waitlist.subscribers (
  id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  source VARCHAR(100) DEFAULT 'landing_page',
  status VARCHAR(20) DEFAULT 'active',
  drip_day_sent INT,                  -- last drip day sent; null means none
  last_sent_at TIMESTAMP WITH TIME ZONE,
  user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL
);

-- email_events table (engagement tracking)
CREATE TABLE IF NOT EXISTS waitlist.email_events (
  id BIGSERIAL PRIMARY KEY,
  subscriber_id BIGINT REFERENCES waitlist.subscribers(id) ON DELETE CASCADE,
  email_id VARCHAR(255),
  event_type VARCHAR(50),
  event_data JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- admin_users table (separate from regular users)
CREATE TABLE IF NOT EXISTS waitlist.admin_users (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  role VARCHAR(50) DEFAULT 'admin',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Grant permissions on tables to service_role
GRANT ALL ON waitlist.subscribers TO service_role;
GRANT ALL ON waitlist.email_events TO service_role;
GRANT ALL ON waitlist.admin_users TO service_role;

-- Grant permissions on sequences to service_role
GRANT ALL ON SEQUENCE waitlist.subscribers_id_seq TO service_role;
GRANT ALL ON SEQUENCE waitlist.email_events_id_seq TO service_role;
GRANT ALL ON SEQUENCE waitlist.admin_users_id_seq TO service_role;

-- Enable Row Level Security
ALTER TABLE waitlist.subscribers ENABLE ROW LEVEL SECURITY;
ALTER TABLE waitlist.email_events ENABLE ROW LEVEL SECURITY;
ALTER TABLE waitlist.admin_users ENABLE ROW LEVEL SECURITY;

-- Admin-only access policies
DO $$ BEGIN
  CREATE POLICY "Admins can view all subscribers" ON waitlist.subscribers
    FOR ALL USING (
      EXISTS (
        SELECT 1 FROM waitlist.admin_users 
        WHERE admin_users.user_id = auth.uid()
      )
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY "Admins can view all email events" ON waitlist.email_events
    FOR ALL USING (
      EXISTS (
        SELECT 1 FROM waitlist.admin_users 
        WHERE admin_users.user_id = auth.uid()
      )
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
  CREATE POLICY "Admins can manage admin users" ON waitlist.admin_users
    FOR ALL USING (
      EXISTS (
        SELECT 1 FROM waitlist.admin_users 
        WHERE admin_users.user_id = auth.uid()
      )
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_waitlist_subscribers_email ON waitlist.subscribers(email);
CREATE INDEX IF NOT EXISTS idx_waitlist_subscribers_subscribed_at ON waitlist.subscribers(subscribed_at);
CREATE INDEX IF NOT EXISTS idx_waitlist_subscribers_status_drip ON waitlist.subscribers(status, drip_day_sent);
CREATE INDEX IF NOT EXISTS idx_waitlist_email_events_subscriber_id ON waitlist.email_events(subscriber_id);
CREATE INDEX IF NOT EXISTS idx_waitlist_email_events_created_at ON waitlist.email_events(created_at);
CREATE INDEX IF NOT EXISTS idx_waitlist_admin_users_user_id ON waitlist.admin_users(user_id);

-- Confirm setup
SELECT 'Database schema created/updated successfully!' as status;



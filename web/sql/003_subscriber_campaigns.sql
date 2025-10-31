-- Waitlist subscriber campaigns (parallel drips per campaign)
-- Create table
CREATE TABLE IF NOT EXISTS waitlist.subscriber_campaigns (
  id BIGSERIAL PRIMARY KEY,
  subscriber_id BIGINT NOT NULL REFERENCES waitlist.subscribers(id) ON DELETE CASCADE,
  campaign TEXT NOT NULL, -- e.g., 'mindmirror', 'uye'
  subscribed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  status VARCHAR(20) DEFAULT 'active',
  drip_day_sent INTEGER DEFAULT -1,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Uniqueness: one active row per (subscriber, campaign)
CREATE UNIQUE INDEX IF NOT EXISTS uq_subscriber_campaign ON waitlist.subscriber_campaigns(subscriber_id, campaign);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_campaign_status ON waitlist.subscriber_campaigns(campaign, status);
CREATE INDEX IF NOT EXISTS idx_campaign_drip ON waitlist.subscriber_campaigns(drip_day_sent);

-- Grants
GRANT ALL ON waitlist.subscriber_campaigns TO service_role;
GRANT ALL ON SEQUENCE waitlist.subscriber_campaigns_id_seq TO service_role;

-- RLS
ALTER TABLE waitlist.subscriber_campaigns ENABLE ROW LEVEL SECURITY;
-- Admin policy mirrors others (optional; manage via service role in practice)
CREATE POLICY "Admins can view all campaigns" ON waitlist.subscriber_campaigns
  FOR ALL USING (
    EXISTS (
      SELECT 1 FROM waitlist.admin_users 
      WHERE admin_users.user_id = auth.uid()
    )
  );



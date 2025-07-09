-- Migration: Add drip campaign support to existing waitlist
-- Run this if you already have the waitlist schema set up

-- Add drip_day_sent column to existing subscribers table
ALTER TABLE waitlist.subscribers 
ADD COLUMN IF NOT EXISTS drip_day_sent INTEGER DEFAULT 0;

-- Set all existing subscribers to day 0 (welcome email)
UPDATE waitlist.subscribers 
SET drip_day_sent = 0 
WHERE drip_day_sent IS NULL;

-- Add index for drip day queries
CREATE INDEX IF NOT EXISTS idx_subscribers_drip_day_sent ON waitlist.subscribers(drip_day_sent);

-- Confirm migration
SELECT 
  'Migration completed!' as status,
  COUNT(*) as total_subscribers,
  COUNT(CASE WHEN drip_day_sent = 0 THEN 1 END) as subscribers_at_day_0
FROM waitlist.subscribers; 
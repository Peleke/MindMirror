-- Add metadata column to vouchers table for storing additional context
-- This allows us to store program_id and other data with vouchers

ALTER TABLE waitlist.vouchers
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}'::jsonb;

-- Add an index for efficient metadata queries
CREATE INDEX IF NOT EXISTS idx_vouchers_metadata ON waitlist.vouchers USING gin(metadata);

-- Add a comment explaining the metadata column
COMMENT ON COLUMN waitlist.vouchers.metadata IS 'JSON object for storing additional voucher context (e.g., program_id for workout programs)';

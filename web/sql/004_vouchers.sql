BEGIN;

CREATE TABLE IF NOT EXISTS waitlist.vouchers (
  id BIGSERIAL PRIMARY KEY,
  code TEXT UNIQUE NOT NULL,
  campaign TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'unused',
  assigned_email TEXT,
  stripe_payment_intent_id TEXT,
  max_redemptions INTEGER DEFAULT 1,
  expires_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  redeemed_at TIMESTAMPTZ,
  redeemed_by UUID REFERENCES auth.users(id)
);

CREATE TABLE IF NOT EXISTS waitlist.program_enrollments (
  id BIGSERIAL PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  campaign TEXT NOT NULL,
  voucher_id BIGINT REFERENCES waitlist.vouchers(id) ON DELETE SET NULL,
  source TEXT NOT NULL DEFAULT 'email',
  status TEXT NOT NULL DEFAULT 'active',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_vouchers_code ON waitlist.vouchers(code);
CREATE INDEX IF NOT EXISTS idx_vouchers_assigned_email ON waitlist.vouchers(assigned_email);
CREATE INDEX IF NOT EXISTS idx_vouchers_status_campaign ON waitlist.vouchers(status, campaign);
CREATE INDEX IF NOT EXISTS idx_enrollments_user_campaign ON waitlist.program_enrollments(user_id, campaign);

GRANT ALL ON waitlist.vouchers TO service_role;
GRANT ALL ON waitlist.program_enrollments TO service_role;
GRANT ALL ON SEQUENCE waitlist.vouchers_id_seq TO service_role;
GRANT ALL ON SEQUENCE waitlist.program_enrollments_id_seq TO service_role;

ALTER TABLE waitlist.vouchers ENABLE ROW LEVEL SECURITY;
ALTER TABLE waitlist.program_enrollments ENABLE ROW LEVEL SECURITY;

COMMIT;

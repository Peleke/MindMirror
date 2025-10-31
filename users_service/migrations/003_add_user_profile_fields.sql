-- Migration: Add user profile fields for email-based lookup and display
-- File: 003_add_user_profile_fields.sql

BEGIN;

-- Add email, first_name, and last_name columns to users table
ALTER TABLE users.users 
ADD COLUMN IF NOT EXISTS email VARCHAR(255),
ADD COLUMN IF NOT EXISTS first_name VARCHAR(100),
ADD COLUMN IF NOT EXISTS last_name VARCHAR(100);

-- Add index on email for efficient lookup
CREATE INDEX IF NOT EXISTS idx_users_email ON users.users(email);

-- Add unique constraint on email (allowing nulls)
CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique 
ON users.users(email) 
WHERE email IS NOT NULL;

COMMIT; 
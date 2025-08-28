-- Create the users schema
CREATE SCHEMA IF NOT EXISTS users;

-- Create the service_type enum
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'service_type' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'users')) THEN
        CREATE TYPE users.service_type AS ENUM (
            'meals',
            'practice',
            'shadow_boxing',
            'fitness_db',
            'programs'
        );
    END IF;
END$$;

-- Create the services table
-- This table stores metadata about the microservices that can interact with the users service.
CREATE TABLE IF NOT EXISTS users.services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name users.service_type NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);
CREATE INDEX IF NOT EXISTS idx_services_name ON users.services(name);


-- Create the users table
CREATE TABLE IF NOT EXISTS users.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    supabase_id VARCHAR(255) UNIQUE NOT NULL,
    keycloak_id VARCHAR(255) UNIQUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
    -- No email or PII here, managed by Supabase/Keycloak
);
CREATE INDEX IF NOT EXISTS idx_users_supabase_id ON users.users(supabase_id);
CREATE INDEX IF NOT EXISTS idx_users_keycloak_id ON users.users(keycloak_id);


-- Create the user_services junction table
-- This table links users to the services they are associated with.
CREATE TABLE IF NOT EXISTS users.user_services (
    user_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES users.services(id) ON DELETE CASCADE, -- Changed from VARCHAR(50) to UUID, and FK reference
    active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    PRIMARY KEY (user_id, service_id)
);
CREATE INDEX IF NOT EXISTS idx_user_services_user_id ON users.user_services(user_id);
CREATE INDEX IF NOT EXISTS idx_user_services_service_id ON users.user_services(service_id);


-- Create the schedulables table
-- This table stores virtual "schedulable" entities aggregated from various services.
CREATE TABLE IF NOT EXISTS users.schedulables (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    service_id UUID NOT NULL REFERENCES users.services(id) ON DELETE CASCADE, -- Changed from VARCHAR(50) to UUID, and FK reference
    name VARCHAR(256) NOT NULL,
    description TEXT,
    entity_id UUID NOT NULL, -- This is the ID of the entity in the originating microservice
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);
CREATE INDEX IF NOT EXISTS idx_schedulables_user_id ON users.schedulables(user_id);
CREATE INDEX IF NOT EXISTS idx_schedulables_service_id ON users.schedulables(service_id);
CREATE INDEX IF NOT EXISTS idx_schedulables_entity_id ON users.schedulables(entity_id);


-- Function to update modified_at timestamp
CREATE OR REPLACE FUNCTION users.update_modified_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.modified_at = clock_timestamp();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for modified_at updates (ensure these are idempotent or drop before creating)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_users_modified_at') THEN
        CREATE TRIGGER update_users_modified_at
        BEFORE UPDATE ON users.users
        FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_services_modified_at') THEN
        CREATE TRIGGER update_services_modified_at
        BEFORE UPDATE ON users.services
        FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_user_services_modified_at') THEN
        CREATE TRIGGER update_user_services_modified_at
        BEFORE UPDATE ON users.user_services
        FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_schedulables_modified_at') THEN
        CREATE TRIGGER update_schedulables_modified_at
        BEFORE UPDATE ON users.schedulables
        FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column();
    END IF;
END$$;

-- Seed initial services if they don't exist
-- Note: `id` is now auto-generated UUID. `name` is the enum value.
INSERT INTO users.services (name, description)
VALUES
    ('meals', 'Nutrition and meal planning service'),
    ('practice', 'Skill and habit practice tracking service'),
    ('shadow_boxing', 'Shadow boxing workout and technique service'),
    ('fitness_db', 'Exercise and workout database service'),
    ('programs', 'Structured fitness and wellness programs service')
ON CONFLICT (name) DO NOTHING;

-- Example: How to query for a service by its name (which is the enum value)
-- SELECT id FROM users.services WHERE name = 'meals'; 
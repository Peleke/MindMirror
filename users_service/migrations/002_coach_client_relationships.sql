-- Add role and domain enums and coach_client_relationships table

-- Create role enum if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'role_enum' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'users')) THEN
        CREATE TYPE users.role_enum AS ENUM ('coach', 'client', 'admin');
    END IF;
END$$;

-- Create domain enum if not exists  
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'domain_enum' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'users')) THEN
        CREATE TYPE users.domain_enum AS ENUM ('meals', 'practices', 'habits', 'journal');
    END IF;
END$$;

-- Create association status enum if not exists
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'association_status_enum' AND typnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'users')) THEN
        CREATE TYPE users.association_status_enum AS ENUM ('pending', 'accepted', 'rejected', 'terminated');
    END IF;
END$$;

-- Create user_roles table if not exists
CREATE TABLE IF NOT EXISTS users.user_roles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    role users.role_enum NOT NULL,
    domain users.domain_enum NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE(user_id, role, domain)
);

CREATE INDEX IF NOT EXISTS idx_user_roles_user_id ON users.user_roles(user_id);
CREATE INDEX IF NOT EXISTS idx_user_roles_role ON users.user_roles(role);
CREATE INDEX IF NOT EXISTS idx_user_roles_domain ON users.user_roles(domain);

-- Create coach_client_relationships table (new structure for the coaching plan)
CREATE TABLE IF NOT EXISTS users.coach_client_relationships (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coach_user_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    client_user_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    status users.association_status_enum NOT NULL DEFAULT 'pending',
    requested_by TEXT NOT NULL CHECK (requested_by IN ('coach', 'client')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE(coach_user_id, client_user_id)
);

CREATE INDEX IF NOT EXISTS idx_coach_client_relationships_coach_user_id ON users.coach_client_relationships(coach_user_id);
CREATE INDEX IF NOT EXISTS idx_coach_client_relationships_client_user_id ON users.coach_client_relationships(client_user_id);
CREATE INDEX IF NOT EXISTS idx_coach_client_relationships_status ON users.coach_client_relationships(status);

-- Create coach_client_associations table if not exists (existing structure)
CREATE TABLE IF NOT EXISTS users.coach_client_associations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    coach_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    client_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    requester_id UUID NOT NULL REFERENCES users.users(id) ON DELETE CASCADE,
    domain users.domain_enum NOT NULL,
    status users.association_status_enum NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    modified_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    UNIQUE(coach_id, client_id, domain)
);

CREATE INDEX IF NOT EXISTS idx_coach_client_associations_coach_id ON users.coach_client_associations(coach_id);
CREATE INDEX IF NOT EXISTS idx_coach_client_associations_client_id ON users.coach_client_associations(client_id);
CREATE INDEX IF NOT EXISTS idx_coach_client_associations_domain ON users.coach_client_associations(domain);

-- Add triggers for modified_at updates
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_user_roles_modified_at') THEN
        CREATE TRIGGER update_user_roles_modified_at
        BEFORE UPDATE ON users.user_roles
        FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_coach_client_relationships_modified_at') THEN
        CREATE TRIGGER update_coach_client_relationships_modified_at
        BEFORE UPDATE ON users.coach_client_relationships
        FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column();
    END IF;
    
    IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'update_coach_client_associations_modified_at') THEN
        CREATE TRIGGER update_coach_client_associations_modified_at
        BEFORE UPDATE ON users.coach_client_associations
        FOR EACH ROW EXECUTE FUNCTION users.update_modified_at_column();
    END IF;
END$$; 
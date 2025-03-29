-- Disable foreign key checks temporarily to avoid dependency issues
SET session_replication_role = 'replica';

-- Drop all views
DROP VIEW IF EXISTS fraud_detection_performance CASCADE;

-- Drop all functions
DROP FUNCTION IF EXISTS insert_transaction CASCADE;

-- Drop all tables
DROP TABLE IF EXISTS fraud_predictions CASCADE;
DROP TABLE IF EXISTS ml_models CASCADE;
DROP TABLE IF EXISTS transactions CASCADE;

-- Drop custom types if any exist
DO $$
DECLARE
    type_rec RECORD;
BEGIN
    FOR type_rec IN (SELECT typname FROM pg_type JOIN pg_namespace ON pg_type.typnamespace = pg_namespace.oid WHERE nspname = 'public' AND typtype = 'c')
    LOOP
        EXECUTE 'DROP TYPE IF EXISTS ' || type_rec.typname || ' CASCADE;';
    END LOOP;
END$$;

-- Drop sequences if any exist
DO $$
DECLARE
    seq_rec RECORD;
BEGIN
    FOR seq_rec IN (SELECT sequence_name FROM information_schema.sequences WHERE sequence_schema = 'public')
    LOOP
        EXECUTE 'DROP SEQUENCE IF EXISTS ' || seq_rec.sequence_name || ' CASCADE;';
    END LOOP;
END$$;

-- Reset foreign key checks
SET session_replication_role = 'origin';

-- Complete cleanup message
DO $$
BEGIN
    RAISE NOTICE 'Database completely cleaned up';
END $$;
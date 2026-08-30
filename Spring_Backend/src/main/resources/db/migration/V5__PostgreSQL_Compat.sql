-- V5: PostgreSQL compatibility patches
-- Adds missing audit/timestamp columns to existing tables
-- and patches reserved-word column names for PostgreSQL compatibility

-- Add auditing columns to hospital (if not present)
ALTER TABLE hospital
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Add auditing columns to app_user (if not present)
ALTER TABLE app_user
    ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Rename backtick-quoted `precision` column to double-quoted version for PostgreSQL
-- (H2 in MySQL mode allows backticks; PostgreSQL requires double quotes)
-- We use a safe rename only if the column exists with the old name
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'model_version' AND column_name = 'precision'
    ) THEN
        ALTER TABLE model_version RENAME COLUMN "precision" TO precision_score;
    END IF;
END $$;

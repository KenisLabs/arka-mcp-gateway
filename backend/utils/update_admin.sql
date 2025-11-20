-- Update Admin User Email and Password
--
-- IMPORTANT: This is a reference SQL file for direct database updates.
-- For production use, we recommend using the Python script (update_admin.py)
-- which handles password hashing automatically.
--
-- Usage with Docker:
--   docker-compose exec postgres psql -U postgres -d arka_mcp_gateway -f /path/to/update_admin.sql
--
-- Usage with local PostgreSQL:
--   psql -U postgres -d arka_mcp_gateway -f update_admin.sql

-- ============================================================================
-- STEP 1: View current admin user
-- ============================================================================

SELECT id, email, name, role, created_at
FROM users
WHERE role = 'admin';


-- ============================================================================
-- STEP 2: Generate bcrypt hash for new password
-- ============================================================================

-- You must generate a bcrypt hash for the password using Python:
--
-- python3 -c "import bcrypt; print(bcrypt.hashpw(b'your_new_password', bcrypt.gensalt()).decode())"
--
-- Copy the output hash and use it in STEP 3 below.
--
-- Example output:
-- $2b$12$abcdefghijklmnopqrstuvwxyz1234567890ABCDEFGHIJKLMNOP


-- ============================================================================
-- STEP 3: Update admin email and/or password
-- ============================================================================

-- Option A: Update BOTH email and password
UPDATE users
SET
    email = 'admin@newdomain.com',
    password_hash = '$2b$12$YOUR_GENERATED_BCRYPT_HASH_HERE'
WHERE role = 'admin';

-- Option B: Update ONLY email
-- UPDATE users
-- SET email = 'admin@newdomain.com'
-- WHERE role = 'admin';

-- Option C: Update ONLY password
-- UPDATE users
-- SET password_hash = '$2b$12$YOUR_GENERATED_BCRYPT_HASH_HERE'
-- WHERE role = 'admin';


-- ============================================================================
-- STEP 4: Verify the update
-- ============================================================================

SELECT id, email, name, role, updated_at
FROM users
WHERE role = 'admin';


-- ============================================================================
-- NOTES
-- ============================================================================

-- Security Best Practices:
-- 1. Always use bcrypt to hash passwords (NEVER store plain text)
-- 2. Use strong passwords (minimum 12 characters, mix of upper/lower/numbers/symbols)
-- 3. Change default credentials immediately after deployment
-- 4. Store this file securely (contains sensitive operations)
-- 5. Use the Python script (update_admin.py) for easier, safer updates

-- Troubleshooting:
-- - If no admin user exists, check if bootstrap was run
-- - If multiple admin users exist, specify which one to update:
--   UPDATE users SET email = '...' WHERE id = 1 AND role = 'admin';
-- - If password hash is invalid, user won't be able to log in
--   (re-run with correct bcrypt hash)

-- Example bcrypt hash generation with Python:
-- $ python3 -c "import bcrypt; password = b'MySecurePassword123!'; print(bcrypt.hashpw(password, bcrypt.gensalt()).decode())"
-- Output: $2b$12$6N8xV4u9Y.J7rC1XH8pXoO8aB8q6G1E8wF3D7m2vR9pL4kT6sN8aG

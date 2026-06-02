-- Premium Service Directory Platform - Initial Migration (Down)
-- Drop triggers first
DROP TRIGGER IF EXISTS update_pipedrive_contacts_updated_at ON pipedrive_contacts;
DROP TRIGGER IF EXISTS update_payments_updated_at ON payments;
DROP TRIGGER IF EXISTS update_categories_updated_at ON categories;
DROP TRIGGER IF EXISTS update_listings_updated_at ON listings;
DROP TRIGGER IF EXISTS update_users_updated_at ON users;

-- Drop function
DROP FUNCTION IF EXISTS update_updated_at_column();

-- Drop tables in reverse order of dependencies
DROP TABLE IF EXISTS pipedrive_contacts;
DROP TABLE IF EXISTS yoti_verifications;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS listing_images;
DROP TABLE IF EXISTS listings;
DROP TABLE IF EXISTS categories;
DROP TABLE IF EXISTS users;

-- Drop enum types
DROP TYPE IF EXISTS payment_method;
DROP TYPE IF EXISTS payment_status;
DROP TYPE IF EXISTS listing_category;
DROP TYPE IF EXISTS listing_status;
DROP TYPE IF EXISTS user_role;

-- Drop extension
DROP EXTENSION IF EXISTS "uuid-ossp";
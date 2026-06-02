-- Premium Service Directory Platform - Initial Migration
-- Create extension for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create enum types
CREATE TYPE user_role AS ENUM ('user', 'admin', 'moderator', 'service_provider');
CREATE TYPE listing_status AS ENUM ('draft', 'pending', 'active', 'paused', 'suspended', 'deleted');
CREATE TYPE listing_category AS ENUM (
    'PLUMBING', 'ELECTRICAL', 'HVAC', 'CLEANING', 'LANDSCAPING',
    'CONSTRUCTION', 'AUTOMOTIVE', 'HEALTHCARE', 'LEGAL', 'ACCOUNTING',
    'REAL_ESTATE', 'HOME_IMPROVEMENT', 'PET_CARE', 'EVENT_PLANNING',
    'EDUCATION', 'FITNESS', 'BEAUTY', 'TECHNOLOGY', 'OTHER'
);
CREATE TYPE payment_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled');
CREATE TYPE payment_method AS ENUM ('credit_card', 'debit_card', 'ach_transfer', 'paypal', 'ccbill');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    roles user_role[] DEFAULT ARRAY['user'],
    marketing_opt_in BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified_at TIMESTAMP,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_deleted_at ON users(deleted_at);
CREATE INDEX idx_users_roles ON users USING GIN(roles);

-- Listings table
CREATE TABLE listings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category listing_category NOT NULL,
    status listing_status DEFAULT 'draft',
    price DECIMAL(10, 2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'USD',
    location VARCHAR(500),
    coordinates JSONB,
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    tags VARCHAR(50)[],
    owner_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    age_verified BOOLEAN DEFAULT FALSE,
    view_count INTEGER DEFAULT 0,
    is_featured BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_listings_title ON listings(title);
CREATE INDEX idx_listings_category ON listings(category);
CREATE INDEX idx_listings_status ON listings(status);
CREATE INDEX idx_listings_owner ON listings(owner_id);
CREATE INDEX idx_listings_location ON listings(location);
CREATE INDEX idx_listings_price ON listings(price);
CREATE INDEX idx_listings_created_at ON listings(created_at DESC);

-- Categories table
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    icon_url VARCHAR(255),
    display_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_categories_code ON categories(code);
CREATE INDEX idx_categories_active ON categories(is_active);

-- Listing images table
CREATE TABLE listing_images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    listing_id UUID NOT NULL REFERENCES listings(id) ON DELETE CASCADE,
    url VARCHAR(500) NOT NULL,
    alt_text VARCHAR(255),
    display_order INTEGER DEFAULT 0,
    width INTEGER,
    height INTEGER,
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_listing_images_listing ON listing_images(listing_id);
CREATE INDEX idx_listing_images_primary ON listing_images(listing_id, is_primary) WHERE is_primary = TRUE;

-- Payments table
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    listing_id UUID REFERENCES listings(id) ON DELETE SET NULL,
    amount DECIMAL(10, 2) NOT NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    status payment_status DEFAULT 'pending',
    method payment_method NOT NULL,
    external_transaction_id VARCHAR(255) UNIQUE,
    payment_intent_id VARCHAR(255),
    card_last4 VARCHAR(4),
    card_brand VARCHAR(20),
    failure_reason TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_listing ON payments(listing_id);
CREATE INDEX idx_payments_status ON payments(status);
CREATE INDEX idx_payments_external_id ON payments(external_transaction_id);
CREATE INDEX idx_payments_created_at ON payments(created_at DESC);

-- Yoti verification table
CREATE TABLE yoti_verifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_id VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    age INTEGER,
    document_type VARCHAR(50),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_yoti_user ON yoti_verifications(user_id);
CREATE INDEX idx_yoti_session ON yoti_verifications(session_id);

-- Pipedrive integration table
CREATE TABLE pipedrive_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    pipedrive_person_id VARCHAR(100),
    pipedrive_deal_id VARCHAR(100),
    email VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_pipedrive_email ON pipedrive_contacts(email);
CREATE INDEX idx_pipedrive_person ON pipedrive_contacts(pipedrive_person_id);

-- Create updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply updated_at triggers
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_listings_updated_at
    BEFORE UPDATE ON listings
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_categories_updated_at
    BEFORE UPDATE ON categories
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_payments_updated_at
    BEFORE UPDATE ON payments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_pipedrive_contacts_updated_at
    BEFORE UPDATE ON pipedrive_contacts
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Insert default categories
INSERT INTO categories (code, name, description, display_order) VALUES
    ('PLUMBING', 'Plumbing Services', 'Professional plumbing services for residential and commercial', 1),
    ('ELECTRICAL', 'Electrical Services', 'Licensed electrical services for all your needs', 2),
    ('HVAC', 'HVAC Services', 'Heating, ventilation, and air conditioning services', 3),
    ('CLEANING', 'Cleaning Services', 'Professional residential and commercial cleaning', 4),
    ('LANDSCAPING', 'Landscaping Services', 'Lawn care, landscaping, and outdoor services', 5),
    ('CONSTRUCTION', 'Construction Services', 'General and specialized construction work', 6),
    ('AUTOMOTIVE', 'Automotive Services', 'Auto repair, maintenance, and detailing', 7),
    ('HEALTHCARE', 'Healthcare Services', 'Medical and health-related services', 8),
    ('LEGAL', 'Legal Services', 'Attorney and legal consultation services', 9),
    ('ACCOUNTING', 'Accounting Services', 'Bookkeeping, tax, and accounting services', 10),
    ('REAL_ESTATE', 'Real Estate Services', 'Property sales, rental, and management', 11),
    ('HOME_IMPROVEMENT', 'Home Improvement', 'Renovation, remodeling, and repair services', 12),
    ('PET_CARE', 'Pet Care Services', 'Pet grooming, sitting, and veterinary care', 13),
    ('EVENT_PLANNING', 'Event Planning', 'Event coordination and planning services', 14),
    ('EDUCATION', 'Education Services', 'Tutoring, coaching, and educational programs', 15),
    ('FITNESS', 'Fitness Services', 'Personal training and fitness coaching', 16),
    ('BEAUTY', 'Beauty Services', 'Salon, spa, and beauty treatment services', 17),
    ('TECHNOLOGY', 'Technology Services', 'IT support, web development, and tech services', 18),
    ('OTHER', 'Other Services', 'Miscellaneous professional services', 19);

-- Create admin user (password: Admin123!)
INSERT INTO users (email, password, first_name, last_name, roles, is_active, email_verified_at)
VALUES (
    'admin@premiumdirectory.com',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYfZRXDz.HW',
    'System',
    'Administrator',
    ARRAY['admin'],
    TRUE,
    CURRENT_TIMESTAMP
);

COMMENT ON TABLE users IS 'User accounts for the Premium Service Directory Platform';
COMMENT ON TABLE listings IS 'Service listings posted by users';
COMMENT ON TABLE categories IS 'Service categories for listings';
COMMENT ON TABLE listing_images IS 'Images associated with listings';
COMMENT ON TABLE payments IS 'Payment transactions';
COMMENT ON TABLE yoti_verifications IS 'Yoti age verification records';
COMMENT ON TABLE pipedrive_contacts IS 'Pipedrive CRM integration contacts';

-- Script to create users table for AgentLM
-- Run this in your PostgreSQL database (pgAdmin query tool)

CREATE EXTENSION IF NOT EXISTS "pgcrypto"; -- For gen_random_uuid() if needed, though Postgres 13+ has it natively usually.

CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Login Credentials
    email VARCHAR(255) NOT NULL UNIQUE,
    phone VARCHAR(50) UNIQUE, -- Unique phone as requested
    password_hash VARCHAR(255) NOT NULL,
    
    -- User Profile
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20), -- 'm', 'f', 'o', etc.
    age INTEGER,
    
    -- Status
    is_active BOOLEAN DEFAULT true
);

-- Index for faster lookups
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);

-- Comment describing the table
COMMENT ON TABLE users IS 'Stores user accounts for the AgentLM supermarket application.';

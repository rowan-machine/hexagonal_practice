-- Initialize warehouse database schema
-- This script runs automatically when the warehouse container starts

-- Create warehouse database (already exists, but ensure it's ready)
\c warehouse;

-- Note: Tables will be created by db_bootstrap.py
-- This file can be used for additional initialization if needed


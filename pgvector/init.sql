-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create schema if not exists
CREATE SCHEMA IF NOT EXISTS ai;

-- Grant necessary permissions
GRANT ALL PRIVILEGES ON DATABASE agno_vectordb TO agno_user;
GRANT ALL PRIVILEGES ON SCHEMA ai TO agno_user; 

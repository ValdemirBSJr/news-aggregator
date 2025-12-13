--- database/migrations/001_init.sql ---
-- basic schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";


CREATE TABLE IF NOT EXISTS news_raw (
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
source TEXT,
title TEXT,
description TEXT,
url TEXT UNIQUE,
published_at TIMESTAMP,
content TEXT,
fetched_at TIMESTAMP DEFAULT now()
);
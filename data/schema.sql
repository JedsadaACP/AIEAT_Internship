-- FORCE SQLITE TO RESPECT FOREIGN KEY CONSTRAINTS
PRAGMA foreign_keys = ON;

-- ==========================================
-- 1. MASTER STATUS (Central Status Dictionary)
-- ==========================================
CREATE TABLE IF NOT EXISTS master_status (
    status_id INTEGER PRIMARY KEY AUTOINCREMENT,
    status_name TEXT NOT NULL,   -- e.g. "Online", "New", "Active"
    status_group TEXT NOT NULL,  -- e.g. 'Source', 'Article', 'System'
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);

-- ==========================================
-- 2. MODELS (AI Model List)
-- ==========================================
CREATE TABLE IF NOT EXISTS models (
    model_id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    file_path TEXT NOT NULL,      -- Local path or API string
    model_type TEXT DEFAULT 'local', -- 'local', 'cloud'
    max_tokens INTEGER DEFAULT 4096,
    status_id INTEGER,            -- Active Status ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (status_id) REFERENCES master_status(status_id)
);

-- ==========================================
-- 3. SYSTEM PROFILE (System Configuration)
-- ==========================================
CREATE TABLE IF NOT EXISTS system_profile (
    profile_id INTEGER PRIMARY KEY CHECK (profile_id = 1), -- Singleton
    org_name TEXT,
    threshold_mandatory INTEGER DEFAULT 2,
    threshold_max INTEGER DEFAULT 5,
    active_model_id INTEGER,
    model_name TEXT,                  -- Ollama model name (e.g., 'scb10x/typhoon2.5-qwen3-4b:latest')
    is_new_news INTEGER DEFAULT 1,       -- 1=Yes, 0=No
    is_related INTEGER DEFAULT 1,        -- 1=Yes, 0=No
    auto_scoring_status INTEGER DEFAULT 0, -- 1=On, 0=Off
    auto_translate_status INTEGER DEFAULT 0, -- 1=On, 0=Off
    date_limit_days INTEGER DEFAULT 14,  -- Days back to scrape (1-30)
    threshold INTEGER,                   -- Translation threshold score
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (active_model_id) REFERENCES models(model_id)
);

-- ==========================================
-- 12. USER PROFILES (Profile-based Configuration)
-- ==========================================
CREATE TABLE IF NOT EXISTS user_profiles (
    profile_id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_name TEXT NOT NULL UNIQUE,
    description TEXT,
    active_style_id INTEGER DEFAULT 1,
    is_active INTEGER DEFAULT 0,
    is_system INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (active_style_id) REFERENCES styles(style_id)
);

-- ==========================================
-- 4. TAGS (Keywords & Domains - Scoped by Profile)
-- ==========================================
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL,
    tag_type TEXT DEFAULT 'Keyword', -- 'Keyword' or 'Domain'
    weight_score INTEGER DEFAULT 1,
    status_id INTEGER, -- Active Status ID
    profile_id INTEGER DEFAULT 1, -- FK to user_profiles (added via migration for existing DBs)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    UNIQUE(tag_name, tag_type, profile_id) -- Scoped uniqueness
);

-- ==========================================
-- 5. SOURCES (News Sources)
-- ==========================================
CREATE TABLE IF NOT EXISTS sources (
    source_id INTEGER PRIMARY KEY AUTOINCREMENT,
    domain_name TEXT NOT NULL,
    base_url TEXT NOT NULL UNIQUE,
    scraper_type TEXT DEFAULT 'RSS', -- 'RSS' or 'HTML'
    status_id INTEGER,               -- Online Status ID
    last_checked_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (status_id) REFERENCES master_status(status_id)
);


-- ==========================================
-- 8. STYLES (Output Styles)
-- ==========================================
CREATE TABLE IF NOT EXISTS styles (
    style_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    output_type TEXT DEFAULT 'article',
    tone TEXT DEFAULT 'professional',
    headline_length TEXT DEFAULT 'medium',
    lead_length TEXT DEFAULT 'medium',
    body_length TEXT DEFAULT 'medium',
    analysis_length TEXT DEFAULT 'medium',
    include_keywords INTEGER DEFAULT 1,
    include_lead INTEGER DEFAULT 1,
    include_analysis INTEGER DEFAULT 1,
    include_source INTEGER DEFAULT 1,
    include_hashtags INTEGER DEFAULT 0,
    custom_instructions TEXT,
    is_active INTEGER DEFAULT 0,
    is_default INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==========================================
-- 8. ARTICLES META (News Metadata)
-- ==========================================
CREATE TABLE IF NOT EXISTS articles_meta (
    article_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_id INTEGER,
    url_hash TEXT NOT NULL UNIQUE, -- CHAR(64)
    published_at DATETIME,
    headline TEXT,
    ai_score INTEGER DEFAULT 0,    -- TINYINT
    status_id INTEGER,             -- Read Status ID
    article_url TEXT NOT NULL,
    author_name TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (source_id) REFERENCES sources(source_id),
    FOREIGN KEY (status_id) REFERENCES master_status(status_id)
);

-- ==========================================
-- 9. ARTICLE CONTENT (News Document)
-- ==========================================
CREATE TABLE IF NOT EXISTS article_content (
    article_id INTEGER PRIMARY KEY, -- PK and FK (1-to-1)
    original_content TEXT,          -- Raw Content
    thai_content TEXT,              -- Thai Translation
    ai_reasoning TEXT,
    used_style_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (article_id) REFERENCES articles_meta(article_id) ON DELETE CASCADE,
    FOREIGN KEY (used_style_id) REFERENCES styles(style_id)
);

-- ==========================================
-- 10. ARTICLE TAG MAP (Tag Relationship)
-- ==========================================
CREATE TABLE IF NOT EXISTS article_tag_map (
    map_id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    match_confidence REAL DEFAULT 1.0, -- FLOAT
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (article_id) REFERENCES articles_meta(article_id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id) ON DELETE CASCADE,
    UNIQUE(article_id, tag_id)
);

-- ==========================================
-- 11. LOGS (System Logs)
-- ==========================================
CREATE TABLE IF NOT EXISTS logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    log_level TEXT NOT NULL,      -- 'INFO', 'ERROR', 'WARNING'
    component TEXT NOT NULL,      -- 'Scraper', 'Database', 'AI'
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT
);

-- ==========================================
-- SEED DATA
-- ==========================================

-- Seed Master Statuses (Essential for App to Start)
INSERT OR IGNORE INTO master_status (status_name, status_group, description) VALUES 
('Active', 'General', 'Item is active and usable'),
('Inactive', 'General', 'Item is disabled'),
('New', 'Article', 'Just scraped, waiting for score'),
('Scored', 'Article', 'AI has assigned a score'),
('Translated', 'Article', 'Translation complete'),
('Online', 'Source', 'Website is reachable'),
('Offline', 'Source', 'Website is down');

-- Seed System Profile (Singleton)
INSERT OR IGNORE INTO system_profile (profile_id, org_name) VALUES (1, 'AIEAT Default Org');

-- Seed Default Styles
INSERT OR IGNORE INTO styles (style_id, name, output_type, tone, headline_length, body_length, analysis_length, include_hashtags, is_default, is_active, custom_instructions) VALUES 
(1, 'News Article', 'article', 'professional', 'medium', 'medium', 'medium', 0, 1, 1, 'You are a professional news editor. Synthesize the provided content into a comprehensive, fluent Thai news article. Maintain a neutral, journalistic tone. Structure with clear headings.'),
(2, 'Social Media', 'facebook', 'conversational', 'short', 'short', 'short', 1, 1, 0, 'You are a social media manager for a Tech page. Summarize this news for Facebook/Twitter in Thai. Use an engaging, conversational tone. Use emojis 🚀 and bullet points. Focus on why this matters to the user.'),
 (3, 'Executive Brief', 'summary', 'formal', 'medium', 'short', 'short', 0, 1, 0, NULL);

-- Seed default profiles (use MIN/MAX style_id for flexibility)
-- is_system = 1 protects these from deletion
INSERT OR IGNORE INTO user_profiles (profile_id, profile_name, description, active_style_id, is_active, is_system)
VALUES
(1, 'Technology & AI', 'AI, software, chips, cloud computing', 1, 1, 1),
(2, 'Finance & Markets', 'Stock markets, banking, fintech, crypto', 3, 0, 1),
(3, 'Politics & Policy', 'Government policy, regulation, geopolitics', 1, 0, 1);

-- Seed default tags for Profile 1 (Technology & AI)
INSERT OR IGNORE INTO tags (tag_id, tag_name, tag_type, weight_score, status_id, profile_id)
VALUES
-- Profile 1: Technology & AI keywords
(1, 'A.I.', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 1),
(2, 'LLM', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 1),
(3, 'GPU', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 1),
(4, 'Semiconductor', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 1),
(5, 'Cloud', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 1),
-- Profile 1: Technology & AI domains
(6, 'Technology', 'Domain', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 1),
(7, 'AI Business', 'Domain', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 1),
(8, 'Software Engineering', 'Domain', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 1),
-- Profile 2: Finance & Markets keywords
(9, 'Stock Market', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 2),
(10, 'Banking', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 2),
(11, 'Fintech', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 2),
(12, 'Cryptocurrency', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 2),
(13, 'IPO', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 2),
-- Profile 2: Finance & Markets domains
(14, 'Finance', 'Domain', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 2),
(15, 'Economics', 'Domain', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 2),
(16, 'Investment', 'Domain', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 2),
-- Profile 3: Politics & Policy keywords
(17, 'Government Policy', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 3),
(18, 'Regulation', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 3),
(19, 'Geopolitics', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 3),
(20, 'Trade War', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 3),
(21, 'Election', 'Keyword', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 3),
-- Profile 3: Politics & Policy domains
(22, 'Politics', 'Domain', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 3),
(23, 'Public Policy', 'Domain', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 3),
(24, 'International Relations', 'Domain', 1, (SELECT status_id FROM master_status WHERE status_name = 'Active'), 3);
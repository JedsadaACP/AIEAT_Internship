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
    is_new_news INTEGER DEFAULT 1,       -- 1=Yes, 0=No
    is_related INTEGER DEFAULT 1,        -- 1=Yes, 0=No
    auto_scoring_status INTEGER DEFAULT 0, -- 1=On, 0=Off
    auto_translate_status INTEGER DEFAULT 0, -- 1=On, 0=Off
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (active_model_id) REFERENCES models(model_id)
);

-- ==========================================
-- 4. TAGS (Keywords & Domains)
-- ==========================================
CREATE TABLE IF NOT EXISTS tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL UNIQUE,
    tag_type TEXT DEFAULT 'Keyword', -- 'Keyword' or 'Domain'
    weight_score INTEGER DEFAULT 1,
    status_id INTEGER,               -- Active Status ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (status_id) REFERENCES master_status(status_id)
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
-- 6. STYLES (Output Styles)
-- ==========================================
CREATE TABLE IF NOT EXISTS styles (
    style_id INTEGER PRIMARY KEY AUTOINCREMENT,
    style_name TEXT NOT NULL,
    output_type TEXT DEFAULT 'Translation',
    system_persona TEXT,          -- "You are an editor..."
    status_id INTEGER,            -- Active Status ID
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by TEXT,
    FOREIGN KEY (status_id) REFERENCES master_status(status_id)
);

-- ==========================================
-- 7. STYLE PARAMS (Style Parameters)
-- ==========================================
CREATE TABLE IF NOT EXISTS style_params (
    param_id INTEGER PRIMARY KEY AUTOINCREMENT,
    style_id INTEGER NOT NULL,
    param_key TEXT NOT NULL,      -- e.g. "headline_limit"
    param_value TEXT NOT NULL,
    param_group TEXT,             -- 'structure', 'analysis'
    sort_order INTEGER DEFAULT 0,
    FOREIGN KEY (style_id) REFERENCES styles(style_id) ON DELETE CASCADE
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
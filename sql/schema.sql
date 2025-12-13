-- =========================================================
-- Data-Driven Marketing Engine
-- PostgreSQL Schema
-- =========================================================

-- This table tracks every data extraction run
CREATE TABLE IF NOT EXISTS data_runs (
  id            BIGSERIAL PRIMARY KEY,
  source        TEXT NOT NULL CHECK (source IN ('ga4', 'gsc')),
  brand         TEXT NOT NULL CHECK (brand IN ('dxfferent', 'proxuma')),
  start_date    DATE NOT NULL,
  end_date      DATE NOT NULL,
  extracted_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  notes         TEXT
);

-- ---------------------------------------------------------
-- GA4 Traffic Report
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS traffic_events (
  id            BIGSERIAL PRIMARY KEY,
  run_id        BIGINT NOT NULL REFERENCES data_runs(id) ON DELETE CASCADE,

  page          TEXT NOT NULL,
  source        TEXT NOT NULL,
  medium        TEXT NOT NULL,
  campaign      TEXT,

  sessions      INTEGER NOT NULL CHECK (sessions >= 0),
  users         INTEGER NOT NULL CHECK (users >= 0),
  conversions   INTEGER,

  start_date    DATE NOT NULL,
  end_date      DATE NOT NULL
);

-- ---------------------------------------------------------
-- GA4 Events Report
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS ga4_events (
  id            BIGSERIAL PRIMARY KEY,
  run_id        BIGINT NOT NULL REFERENCES data_runs(id) ON DELETE CASCADE,

  page          TEXT NOT NULL,
  event_name    TEXT NOT NULL,

  event_count   INTEGER NOT NULL CHECK (event_count >= 0),
  users         INTEGER NOT NULL CHECK (users >= 0),

  start_date    DATE NOT NULL,
  end_date      DATE NOT NULL
);

-- ---------------------------------------------------------
-- Google Search Console (page × query)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS search_queries (
  id            BIGSERIAL PRIMARY KEY,
  run_id        BIGINT NOT NULL REFERENCES data_runs(id) ON DELETE CASCADE,

  query         TEXT NOT NULL,
  page          TEXT NOT NULL,

  clicks        INTEGER NOT NULL CHECK (clicks >= 0),
  impressions   INTEGER NOT NULL CHECK (impressions >= 0),
  ctr           DOUBLE PRECISION NOT NULL CHECK (ctr >= 0 AND ctr <= 1),
  position      DOUBLE PRECISION NOT NULL CHECK (position >= 0),

  start_date    DATE NOT NULL,
  end_date      DATE NOT NULL
);

-- ---------------------------------------------------------
-- Helpful indexes for marketing queries
-- ---------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_traffic_events_page
  ON traffic_events (page);

CREATE INDEX IF NOT EXISTS idx_traffic_events_source_medium
  ON traffic_events (source, medium);

CREATE INDEX IF NOT EXISTS idx_ga4_events_page_event
  ON ga4_events (page, event_name);

CREATE INDEX IF NOT EXISTS idx_search_queries_query
  ON search_queries (query);

CREATE INDEX IF NOT EXISTS idx_search_queries_page
  ON search_queries (page);

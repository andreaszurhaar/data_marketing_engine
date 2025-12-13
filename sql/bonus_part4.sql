-- Part 4 Bonus: Feedback loop tables

CREATE TABLE IF NOT EXISTS content_experiments (
  id            BIGSERIAL PRIMARY KEY,
  brand         TEXT NOT NULL CHECK (brand IN ('dxfferent', 'proxuma')),
  goal          TEXT NOT NULL,                 -- e.g. "increase organic visibility"
  topic         TEXT NOT NULL,                 -- e.g. "autotask dispatch calendar"
  content_type  TEXT NOT NULL,                 -- e.g. "blog" or "linkedin"
  title         TEXT NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  published_at  TIMESTAMPTZ,
  url           TEXT,
  notes         TEXT
);

CREATE TABLE IF NOT EXISTS content_feedback (
  id             BIGSERIAL PRIMARY KEY,
  experiment_id  BIGINT NOT NULL REFERENCES content_experiments(id) ON DELETE CASCADE,
  captured_at    TIMESTAMPTZ NOT NULL DEFAULT now(),

  -- Keep this flexible: you can store GA4/GSC deltas, or manual labels
  metric_name    TEXT NOT NULL,                -- e.g. "gsc_clicks_delta", "ga4_sessions_delta", "manual_score"
  metric_value   DOUBLE PRECISION NOT NULL,
  source         TEXT NOT NULL CHECK (source IN ('ga4', 'gsc', 'manual')),
  notes          TEXT
);

CREATE INDEX IF NOT EXISTS idx_experiments_brand_topic
  ON content_experiments (brand, topic);

CREATE INDEX IF NOT EXISTS idx_feedback_experiment
  ON content_feedback (experiment_id);

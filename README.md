# Data‑Driven Marketing Engine

*A practical demonstration of turning GA4 + Google Search Console data into actionable marketing decisions*

---

## Executive Summary (non‑technical)

This project demonstrates how raw analytics data can be transformed into **clear, defensible content decisions**.

Instead of reporting metrics ("X impressions", "Y sessions"), the system answers a more valuable question:

> **“Given what users search for and how they behave on the site, what content should we create next — and why?”**

Using real data from:
- **Google Analytics 4 (GA4)** — what users actually do on the site
- **Google Search Console (GSC)** — what users search for and whether they click

…the project:
1. Detects **where demand exists** (search impressions)
2. Identifies **where performance is weak** (low clicks / CTR)
3. Generates **concrete content ideas** tailored to the brand’s business model
4. Stores those ideas as experiments so performance can be tracked over time

Two brands are used to demonstrate adaptability:
- **Dxfferent** (consultancy / authority model)
- **Proxuma** (SaaS / product‑led model)

---

## Why this is useful (marketing intuition)

Modern marketing teams often struggle with one problem:

> *“We have data — but we don’t know what to do with it.”*

This project bridges that gap by:
- avoiding vanity metrics
- focusing on **opportunity gaps** (high demand, low performance)
- producing output that can be directly handed to content, SEO, or product marketing teams

The result is not a dashboard — it is a **decision engine**.

---

## High‑level architecture

```
GA4 (traffic + events)      GSC (queries + pages)
          │                         │
          ▼                         ▼
     Raw JSON files           Raw JSON files
          │                         │
          ▼                         ▼
   Flattened row JSON   ←   Flattened row JSON
          │
          ▼
     PostgreSQL database
          │
          ▼
 Content idea generator
          │
          ▼
 Structured content ideas + experiment logging
```

Each step is persisted so the pipeline is:
- auditable
- reproducible
- explainable

---

## Repository structure

```
.
├── src/            # Python scripts (fetch, flatten, load, generate)
├── data/           # Raw data, flattened data, generated outputs
├── sql/            # PostgreSQL schema files
├── README.md       # This document
└── .env            # Credentials & DB config (not committed)
```

---

## Part 1 — Data extraction & normalization

### GA4 extraction via MCP (Model Context Protocol)

GA4 data in this project is retrieved via an **MCP-compatible analytics server**, rather than by calling the GA4 API directly from this repository.

#### What MCP does in this project
- Acts as a secure intermediary to Google Analytics 4
- Handles authentication and GA4 API access outside of the project code
- Returns GA4 report results as structured JSON

This design choice allows the repository to:
- avoid embedding Google credentials in application code
- treat GA4 as an external data source
- focus on data normalization, storage, and decision logic rather than API plumbing

#### How the MCP integration is run
1. An MCP analytics server with GA4 access is started separately (outside this repository)
2. GA4 reports are requested via the MCP interface
3. The MCP server returns raw GA4 report JSON
4. That raw JSON is copied and saved locally in the `data/` directory

Example raw GA4 outputs:
- `data/ga4_run_report_<brand>_raw.json`
- `data/ga4_events_<brand>_raw.json`

These files represent the **unmodified GA4 response** and are intentionally preserved as an audit trail.

#### Assumptions
- An MCP analytics server with access to the relevant GA4 properties already exists
- The user has permission to query those GA4 properties
- This project begins at the point where MCP output is available as raw JSON

This separation keeps the scope of the project aligned with the assignment: demonstrating **data engineering and marketing decision-making**, not authentication setup.

### GA4
Two GA4 reports are extracted via an MCP analytics server:

1. **Traffic report**
   - Dimensions: landing page, source, medium
   - Metrics: sessions, users

2. **Events report**
   - Dimensions: landing page, event name
   - Metrics: event count, users

For both reports:
- Raw MCP JSON is saved for traceability
- Data is flattened into row‑based JSON for database ingestion

### Google Search Console

From GSC we extract:
- search query
- page
- clicks
- impressions
- CTR
- average position

This allows us to see **what people are searching for** and **whether our pages win the click**.

---

## Part 2 — PostgreSQL schema & ingestion

### Core tables

| Table | Purpose |
|------|--------|
| `data_runs` | Tracks every extraction/load run (source, brand, date range) |
| `traffic_events` | GA4 traffic performance |
| `ga4_events` | GA4 engagement signals |
| `search_queries` | GSC query × page performance |

The database becomes the **single source of truth** across tools.

---

## Part 3 — Content idea generation (core deliverable)

### The core idea

Part 3 answers this question:

> **“Given real GA4 and GSC data, what content should this brand create next — and why?”**

The generator does *not* guess.
It applies explicit reasoning rules based on marketing best practices.

---

### How opportunities are detected

From GSC we identify queries with:
- **High impressions** → proven demand
- **Low clicks / low CTR** → unmet opportunity

From GA4 we identify:
- pages that already attract traffic
- topic areas the audience responds to

These two signals together form a **content opportunity context**.

---

## Real examples (this project’s output)

### Example 1 — Proxuma (SaaS product)

**Observed data**
- Query: `autotask project management solution`
- Impressions: 344
- Clicks: 0
- Average position: ~3

**Interpretation**
- Google already considers Proxuma relevant
- Users see the result but do not click
- Likely causes: weak title, unclear value proposition, wrong landing page

**Generated content idea**

> **Title:** Autotask Project Management – How Proxuma helps MSPs do it better  
> **Type:** SEO landing page  
> **Why:** 344 impressions, 0 clicks — visible but not chosen  
> **CTA:** Book a demo

**Why this is useful**
- Targets commercial intent
- Improves CTR
- Directly supports product growth

---

### Example 2 — Proxuma (workflow content)

**Observed data**
- Query: `dispatch calendar`
- Impressions: 245
- Clicks: 0
- Avg position: ~4

**Generated idea**

> **Title:** Dispatch Calendar: a practical MSP workflow (template included)  
> **Type:** Blog / workflow guide

**Why chosen**
- Mid‑funnel intent
- Positions Proxuma as operational expert
- Supports product adoption

---

### Example 3 — Dxfferent (consultancy authority)

**Observed data**
- Query: `wat doet een security officer`
- Impressions: 110
- Clicks: 0
- Avg position: ~18

**Generated ideas**

1. **Blog**
   - *“Wat doet een security officer? Responsibilities, pitfalls, and onboarding plan”*

2. **Lead magnet**
   - *“Security Officer Starter Kit (ISO‑aligned checklist)”*

**Why this is useful**
- Matches informational intent
- Builds authority
- Converts readers into consulting leads

---

## Why this meets the Part 3 requirements

Part 3 required:
- Data‑driven content ideas ✔
- Use of GA4 and GSC metrics ✔
- Brand awareness ✔
- Structured, explainable output ✔

The generator:
- references **real numbers** (impressions, clicks, positions)
- produces **explicitly justified decisions**
- can be re‑run whenever new data is loaded

---

## Bonus Part 4 — Feedback loop

To support learning over time, two additional tables are added:

| Table | Purpose |
|------|--------|
| `content_experiments` | Stores proposed/published content |
| `content_feedback` | Stores performance or evaluation signals |

Generated ideas are inserted into `content_experiments`, turning suggestions into **trackable experiments**.

Future process:
1. Publish content
2. Capture GA4/GSC deltas or manual scores
3. Favor topics and formats that historically perform best

This turns the system into a **learning marketing loop**.

---

## How to run the project (technical)

### 1. Create database
```bash
createdb marketing_engine
psql -d marketing_engine -f sql/schema.sql
```

### 2. Load data
```bash
python src/load_ga4_traffic.py
python src/load_ga4_events.py
python src/load_gsc.py
```

### 3. Generate content ideas
```bash
python src/generate_content_ideas.py
```

Output:
```
data/content_ideas_from_db.json
```

### 4. (Bonus) Log experiments
```bash
psql -d marketing_engine -f sql/bonus_part4.sql
python src/insert_experiments_from_ideas.py
```

---

## Key takeaway

This project shows that **marketing analytics becomes valuable only when it informs decisions**.

By explicitly connecting:
- search demand
- user behavior
- business context

…the system turns raw metrics into **clear, defensible content strategy**.

That — not dashboards — is the real value of data‑driven marketing.


# Manotar Project Documentation

This directory contains documentation for the Manotar Mental Health Analytics Platform.

## Directory Structure

- `architecture/` - System architecture diagrams and explanations
- `api/` - API documentation and endpoints
- `setup/` - Setup and installation guides
- `user-guides/` - End-user documentation

## API Versioning

All API endpoints follow the pattern `/api/v1/*` to ensure proper versioning.

If a breaking change is required, new endpoints will be created under `/api/v2/*`.

## Data Privacy & GDPR Compliance

All employee and sentiment data is subject to strict GDPR compliance:
- Data is anonymized where appropriate
- Data retention is limited to 24 months unless explicit consent is given
- Users can request data export and deletion

## Technical Stack

- **Backend**: Flask (Python)
- **Frontend**: Next.js (TypeScript) with App Router
- **Database**: SQLAlchemy ORM
- **Styling**: TailwindCSS
- **Deployment**: Docker / GCP / Heroku

## Maintenance Schedule

This documentation is reviewed quarterly or upon significant architectural changes. 
# Changelog

All notable changes to SwapSpot will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- Repositioned the project as a **portfolio case study** rather than a hosted product. README, CHANGELOG, and the GitHub Pages site now describe SwapSpot as a static showcase backed by inspectable Django source.
- Rewrote `site/index.html` as a polished, responsive, accessible portfolio showcase with light/dark theming, a concept-project disclaimer, full keyboard navigation, and WCAG AA-aligned contrast.
- Reworked `.github/workflows/ci-cd.yml` to a static-only Pages pipeline: validates `site/index.html` and asserts no backend deploy artifacts remain, then deploys `site/` to GitHub Pages from `main`.
- Simplified `SwapSpot/settings.py` back to local-review settings with SQLite only, while keeping lightweight `.env` overrides for local development.
- Updated all dependencies to latest stable versions:
  - Django 5.1.2 → 6.0.5
  - djangorestframework 3.15.2 → 3.17.1
  - Pillow 11.0.0 → 12.2.0
  - cryptography 43.0.3 → 48.0.0
  - asgiref 3.8.1 → 3.11.1
  - cffi 1.17.1 → 2.0.0
  - pycparser 2.22 → 3.0
  - PyMySQL 1.1.1 → 1.1.3
  - sqlparse 0.5.1 → 0.5.5
  - tzdata 2024.2 → 2026.2
- `.gitignore` no longer excludes `**/migrations/` — migration files are now tracked for fresh-clone reliability.

### Added
- Static GitHub Pages portfolio site at `site/index.html` showcasing SwapSpot as a project case study (overview, features, stack, API surface, data flow).
- Missing `add_item.html` template for fresh-clone readiness.
- `0002` migration for `Item.picture` and `User.contact` fields.
- Health regression tests covering templates, API serialization, permissions, and rating signals.
- `.env.example` file documenting local environment variables.
- `CONTRIBUTING.md` with setup, code style, and PR guidelines.
- `CHANGELOG.md` (this file).
- Rewritten `README.md` with logo, quick start, project structure, API reference, and configuration guidance.

### Removed
- `render.yaml` Render Blueprint and `build.sh` deploy script (backend deployment is no longer in scope).
- README "Deployment" section advertising Render hosting; replaced with a "Portfolio Showcase" section describing the static Pages presentation.
- Deployment-only Python packages from `requirements.txt`: `gunicorn`, `whitenoise`, `dj-database-url`, and `psycopg2-binary`.
- Render/PostgreSQL/WhiteNoise configuration from `SwapSpot/settings.py`, including `DATABASE_URL` parsing, Render host handling, WhiteNoise middleware/storage, and production security gates.

### Fixed
- Added `rest_framework` to `INSTALLED_APPS` so DRF endpoints and browsable API work correctly.
- Imported `PermissionDenied` in `views.py` so `delete_item` returns 403 instead of `NameError` on non-POST requests.
- Removed duplicate `item_detail` function (unauthenticated version was dead code shadowed by the `@login_required` version).
- Fixed `UserSerializer` — `full_name` and `profile_picture_url` now use `SerializerMethodField` instead of referencing non-existent model fields.
- Fixed profile redirect namespace in `delete_account` view.

## [0.1.0] — Initial Development

### Added
- User registration with two-step signup flow.
- User profiles with avatar upload, bio, location, and average rating.
- Item listings with title, description, category, condition, price, listing type, and photo.
- Homepage with search and category filtering.
- Item detail page with suggested items.
- Proposal system for exchanges and purchases.
- Transaction and review models.
- Notification system.
- 5-star rating with automatic average calculation via Django signals.
- Django admin interface.
- REST API with 9 ViewSets (users, items, proposals, transactions, reviews, notifications, tags, item-tags, payment-methods).
- Landing page, login, and logout flows.
- Profile settings and account deletion.

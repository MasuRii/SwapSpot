<p align="center">
  <img src="static/svg/swapspot-logo-light.svg" alt="SwapSpot Logo" width="320">
</p>

<h1 align="center">SwapSpot</h1>

<p align="center">
  A community-based item exchange and marketplace platform built with Django.
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#features">Features</a> ·
  <a href="#tech-stack">Tech Stack</a> ·
  <a href="#api">API</a> ·
  <a href="#contributing">Contributing</a>
</p>

---

SwapSpot is a hybrid marketplace where users can list items for sale, propose exchanges (barter), or combine both. It supports user profiles, item discovery, proposal negotiation, reviews, and notifications — all through a Django-powered web application with a REST API.

## Features

- **User Registration & Profiles** — Two-step signup, profile editing, avatar uploads, and average rating display.
- **Item Listings** — Create, edit, and delete items with title, description, category, condition, price, and photo.
- **Search & Browse** — Keyword search, category filtering, and homepage feed of available items.
- **Proposal System** — Send, accept, or reject exchange/purchase proposals between users.
- **Rating & Reviews** — 5-star ratings with automatic average calculation via Django signals.
- **Notifications** — In-app notification system for transaction and proposal updates.
- **REST API** — Full CRUD endpoints for all models via Django REST Framework ViewSets.

## Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Framework | [Django](https://www.djangoproject.com/) | 6.0.5 |
| REST API | [Django REST Framework](https://www.django-rest-framework.org/) | 3.17.1 |
| Database | SQLite3 (dev), PostgreSQL (prod) | — |
| Image Handling | [Pillow](https://python-pillow.org/) | 12.2.0 |
| Python | Python 3.13+ | — |

> See [`requirements.txt`](requirements.txt) for the full dependency list.

## Quick Start

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/MasuRii/SwapSpot.git
cd SwapSpot

# 2. Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables (see Configuration below)
cp .env.example .env

# 5. Run database migrations
python manage.py migrate

# 6. Create a superuser (admin account)
python manage.py createsuperuser

# 7. Start the development server
python manage.py runserver
```

The app will be available at [http://localhost:8000](http://localhost:8000).

### Running Tests

```bash
python manage.py test
```

## Configuration

SwapSpot uses real environment variables first, fills any missing values from a project-root `.env` file if it exists, then applies safe development defaults. Copy `.env.example` to `.env` for local customization:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Production only | Development-only fallback | Django secret key for cryptographic signing. Set a unique value before deployment. |
| `DJANGO_DEBUG` | No | `True` | Enables Django debug mode. Set to `False` in production. |
| `DJANGO_ALLOWED_HOSTS` | When `DJANGO_DEBUG=False` | `""` | Comma-separated list of allowed hostnames. Required in production. |

> ⚠️ **Security:** Production startup fails unless `DJANGO_DEBUG=False` is paired with a unique `DJANGO_SECRET_KEY` and at least one `DJANGO_ALLOWED_HOSTS` entry. Never deploy with the example secret key placeholder.

## Project Structure

```
SwapSpot/
├── SwapSpot/                 # Django project settings & configuration
│   ├── settings.py           # Main settings file
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py               # WSGI entry point
├── exchange/                 # Main application
│   ├── models.py             # Database models (User, Item, Proposal, etc.)
│   ├── views.py              # Template views & DRF ViewSets
│   ├── serializers.py        # DRF serializers
│   ├── forms.py              # Django forms
│   ├── signals.py            # Rating average auto-calculation
│   ├── urls.py               # App URL routes & API router
│   ├── tests.py              # Test suite
│   └── migrations/           # Database migrations
├── templates/exchange/       # HTML templates
├── static/                   # CSS, JS, images, SVGs
│   ├── css/
│   ├── js/
│   ├── images/
│   └── svg/
├── manage.py                 # Django management command
├── requirements.txt          # Python dependencies
└── README.md
```

### URL Routes

| Path | View | Description |
|---|---|---|
| `/` | Landing page | Public landing page |
| `/signup/step1/` | Signup step 1 | Email, username, password |
| `/signup/step2/` | Signup step 2 | Name, location, terms |
| `/login/` | Login | Email/password login |
| `/homepage/` | Home feed | Browse available items |
| `/profile/<username>/` | User profile | View profile, items, ratings |
| `/add-item/` | Add item | Create a new listing |
| `/item/<id>/` | Item detail | View item, see suggestions |
| `/item/<id>/edit/` | Edit item | Modify your listing |
| `/items/<id>/delete/` | Delete item | Remove your listing (POST only) |
| `/settings/` | Profile settings | Edit account details |
| `/delete-account/` | Delete account | Remove account (POST only) |
| `/api/` | DRF API root | Browse all API endpoints |
| `/admin/` | Django admin | Admin interface |

## API

SwapSpot exposes a REST API powered by Django REST Framework. All resource endpoints are available under `/api/`:

| Endpoint | Resource |
|---|---|
| `/api/users/` | Users |
| `/api/items/` | Items |
| `/api/proposals/` | Exchange/purchase proposals |
| `/api/transactions/` | Completed transactions |
| `/api/reviews/` | User reviews |
| `/api/notifications/` | User notifications |
| `/api/tags/` | Item tags |
| `/api/item-tags/` | Item–tag associations |
| `/api/payment-methods/` | Payment methods |
| `/api-auth/` | DRF browsable API authentication |

All ViewSets support standard CRUD operations (`list`, `create`, `retrieve`, `update`, `partial_update`, `destroy`).

## Models

| Model | Key Fields | Description |
|---|---|---|
| `User` | email, username, profile_picture, average_rating | Custom user model (email as username) |
| `Item` | title, description, category, condition, price, listing_type | Marketplace listings |
| `Proposal` | sender, receiver, item, message, status | Exchange/purchase proposals |
| `Transaction` | proposal, amount, transaction_type | Completed transactions |
| `Review` | reviewer, reviewee, transaction, rating, comment | Post-transaction reviews |
| `Rating` | rater, ratee, rating (1–5) | Quick star ratings on profiles |
| `Notification` | user, content, is_read | In-app notifications |
| `Tag` / `ItemTag` | name, item, tag | Item categorization |
| `PaymentMethod` | user, provider, account_details | User payment info |

## Deployment

SwapSpot is configured for production deployment on [Render](https://render.com/) via the included `render.yaml` Blueprint:

- **Web Service** — Gunicorn + WhiteNoise for static files
- **Database** — Render PostgreSQL, auto-configured via `DATABASE_URL`
- **Static Files** — Collected to `staticfiles/` and served with compression

To deploy, push this repository to GitHub/GitLab, then create a Render Blueprint from `render.yaml`.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions, code style guidelines, and pull request process.

## License

This project does not currently have a license. All rights reserved by default. Contact the maintainers for usage permissions.

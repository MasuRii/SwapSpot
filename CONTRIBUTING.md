# Contributing to SwapSpot

Thank you for your interest in contributing to SwapSpot! This guide will help you get set up and submit changes.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- Git

### Development Setup

1. **Fork and clone** the repository:

   ```bash
   git clone https://github.com/<your-username>/SwapSpot.git
   cd SwapSpot
   ```

2. **Create a virtual environment** and activate it:

   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional for defaults, recommended for local customization):

   ```bash
   cp .env.example .env
   ```

   `settings.py` loads `.env` automatically. The defaults are enough for local review; use `.env` only for local values such as `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, or `DJANGO_ALLOWED_HOSTS`.

5. **Run migrations**:

   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (optional, for admin access):

   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**:

   ```bash
   python manage.py runserver
   ```

8. **Verify the setup** by visiting [http://localhost:8000](http://localhost:8000).

## Making Changes

### Branch Naming

Create a feature branch from `main`:

```bash
git checkout -b feature/your-feature-name
```

Use prefixes like `feature/`, `fix/`, `docs/`, or `refactor/` to describe the type of change.

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code.
- Use 4 spaces for indentation (no tabs).
- Keep functions and methods focused — one responsibility per function.
- Use descriptive variable and function names.
- Add docstrings to new classes and non-trivial functions.

### Database Migrations

If you modify models in `exchange/models.py`:

```bash
python manage.py makemigrations exchange
python manage.py migrate
```

**Always commit your migration files** along with the model changes. Migrations are tracked in version control to ensure fresh clones work without running `makemigrations`.

### Writing Tests

Add tests for new features in `exchange/tests.py`. The project uses Django's built-in test framework:

```bash
python manage.py test
```

Ensure all existing tests pass before submitting a pull request.

### Running Checks

Before committing, run Django's system checks:

```bash
python manage.py check
python manage.py test
```

## Submitting a Pull Request

1. **Ensure all tests pass** and there are no Django system check warnings.
2. **Commit your changes** with a clear, descriptive message:

   ```bash
   git commit -m "Add item search by price range"
   ```

3. **Push your branch**:

   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** against the `main` branch with:
   - A clear title describing the change
   - A summary of what was changed and why
   - Any related issue numbers

## Project Conventions

| Area | Convention |
|---|---|
| Templates | Located in `templates/exchange/`, extend `base.html` |
| Static files | CSS in `static/css/`, JS in `static/js/`, images in `static/images/`, SVGs in `static/svg/` |
| URLs | Namespaced under `exchange:` (e.g., `exchange:homepage`) |
| Models | All in `exchange/models.py`, using `AUTH_USER_MODEL = 'exchange.User'` |
| API | DRF ViewSets in `exchange/views.py`, serializers in `exchange/serializers.py` |

## Questions?

If you have questions about contributing, feel free to open an issue on the repository.

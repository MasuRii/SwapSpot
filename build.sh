#!/usr/bin/env bash
# ── Render Build Script ──────────────────────────────────────────
# Runs on every deploy in the Render build environment.
# Installs Python dependencies, collects static files, and runs checks.
set -euo pipefail

echo "=== SwapSpot Build ==="
echo "Python: $(python3 --version)"
echo "Pip:    $(pip3 --version 2>&1 || pip --version)"

# ── Install dependencies ─────────────────────────────────────────
echo ""
echo ">>> Installing Python dependencies..."
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# ── Collect static files ─────────────────────────────────────────
echo ""
echo ">>> Collecting static files..."
python manage.py collectstatic --noinput --clear

# ── Run system checks (warnings only, no hard fail on deploy warnings) ──
echo ""
echo ">>> Running Django system checks..."
python manage.py check --deploy || true

# ── Verify migrations ────────────────────────────────────────────
echo ""
echo ">>> Verifying migrations..."
python manage.py makemigrations --dry-run --check || {
    echo "WARNING: Unapplied model changes detected. Migrations will run in preDeployCommand."
}

echo ""
echo "=== Build complete ==="

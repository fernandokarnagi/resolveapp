#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# ResolveApp – Heroku Deployment Script
# Usage:  ./deploy-heroku.sh [app-name]
#         ./deploy-heroku.sh resolveapp-prod
#
# Prerequisites:
#   - Heroku CLI installed  (brew install heroku)
#   - Logged in             (heroku login)
#   - Git repo initialised  (git init && git add . && git commit -m "init")
# ─────────────────────────────────────────────────────────────────────────────
set -e

APP_NAME="${1:-resolveai}"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ResolveApp Heroku Deployment"
echo "  App: $APP_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# ── 1. Check Heroku CLI ───────────────────────────────────────────────────────
if ! command -v heroku &>/dev/null; then
  echo "✗ Heroku CLI not found. Install: brew install heroku"
  exit 1
fi

# ── 2. Create or use existing app ────────────────────────────────────────────
if heroku apps:info "$APP_NAME" &>/dev/null; then
  echo "✔ Using existing Heroku app: $APP_NAME"
else
  echo "Creating Heroku app: $APP_NAME ..."
  heroku create "$APP_NAME"
fi

# ── 3. Set buildpacks (Node first so frontend builds, then Python for FastAPI)
echo ""
echo "Setting buildpacks..."
heroku buildpacks:clear --app "$APP_NAME" 2>/dev/null || true
heroku buildpacks:add --index 1 heroku/nodejs  --app "$APP_NAME"
heroku buildpacks:add --index 2 heroku/python  --app "$APP_NAME"
echo "  ✔ nodejs (builds React frontend)"
echo "  ✔ python  (runs FastAPI backend)"

# ── 4. Set environment variables ─────────────────────────────────────────────
echo ""
echo "Configuring environment variables..."

# Prompt for MongoDB URL if not already set
CURRENT_MONGO=$(heroku config:get MONGODB_URL --app "$APP_NAME" 2>/dev/null || true)
if [ -z "$CURRENT_MONGO" ]; then
  echo ""
  echo "  ⚠  MONGODB_URL is not set."
  read -rp "  Enter your MongoDB Atlas connection string: " MONGO_URL
  heroku config:set MONGODB_URL="$MONGO_URL" --app "$APP_NAME"
else
  echo "  ✔ MONGODB_URL already set"
fi

# Generate a secret key if not set
CURRENT_SECRET=$(heroku config:get SECRET_KEY --app "$APP_NAME" 2>/dev/null || true)
if [ -z "$CURRENT_SECRET" ]; then
  SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  heroku config:set SECRET_KEY="$SECRET" --app "$APP_NAME"
  echo "  ✔ SECRET_KEY generated"
else
  echo "  ✔ SECRET_KEY already set"
fi

# Fixed config
heroku config:set \
  DATABASE_NAME=resolveapp \
  ALGORITHM=HS256 \
  ACCESS_TOKEN_EXPIRE_MINUTES=1440 \
  NPM_CONFIG_PRODUCTION=false \
  --app "$APP_NAME"

echo "  ✔ App config applied"

# ── 5. Add git remote ─────────────────────────────────────────────────────────
echo ""
echo "Setting git remote..."
if git remote get-url heroku &>/dev/null; then
  git remote set-url heroku "https://git.heroku.com/$APP_NAME.git"
else
  heroku git:remote --app "$APP_NAME"
fi
echo "  ✔ Remote: heroku → https://git.heroku.com/$APP_NAME.git"

# ── 6. Ensure we're on a deployable commit ────────────────────────────────────
if ! git rev-parse --git-dir &>/dev/null; then
  echo ""
  echo "  ✗ Not a git repository. Run:"
  echo "      git init && git add . && git commit -m 'Initial commit'"
  exit 1
fi

# Stage any uncommitted changes (warn only)
if ! git diff-index --quiet HEAD -- 2>/dev/null; then
  echo ""
  echo "  ⚠  You have uncommitted changes. Commit them before deploying."
  echo "     git add . && git commit -m 'Deploy'"
  read -rp "  Continue anyway? (y/N) " confirm
  [[ "$confirm" =~ ^[Yy]$ ]] || exit 1
fi

# ── 7. Deploy ─────────────────────────────────────────────────────────────────
echo ""
echo "Deploying to Heroku..."
echo "  (Node buildpack will run: npm run heroku-postbuild → builds React)"
echo "  (Python buildpack will install backend/requirements.txt)"
echo ""
git push heroku HEAD:main --force

# ── 8. Post-deploy ────────────────────────────────────────────────────────────
echo ""
APP_URL="https://$APP_NAME.herokuapp.com"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅  Deployment complete!"
echo ""
echo "  App URL : $APP_URL"
echo "  API Docs: $APP_URL/docs"
echo ""
echo "  To view logs:  heroku logs --tail --app $APP_NAME"
echo "  To open app:   heroku open --app $APP_NAME"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
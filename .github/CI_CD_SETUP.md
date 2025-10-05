# CI/CD Setup Guide

This project uses GitHub Actions for continuous integration and deployment.

## Workflows

### 1. Backend CI (`backend-ci.yml`)
**Triggers:** Push/PR to `main` or `develop` branches with backend changes

**Steps:**
- Sets up Python 3.11
- Installs dependencies
- Runs linting with flake8
- Runs tests with pytest
- Uploads coverage reports

**Services:**
- PostgreSQL 15
- Redis 7

### 2. Frontend CI (`frontend-ci.yml`)
**Triggers:** Push/PR to `main` or `develop` branches with frontend changes

**Steps:**
- Sets up Node.js 18
- Installs dependencies
- Runs linting (if configured)
- Type checks with TypeScript
- Runs tests
- Builds the app
- Uploads build artifacts

### 3. Deploy (`deploy.yml`)
**Triggers:** Push to `main` branch

**Jobs:**
- `deploy-backend`: Deploys backend to Render
- `deploy-frontend`: Triggers Vercel deployment
- `notify`: Sends deployment status notification

### 4. PR Check (`pr-check.yml`)
**Triggers:** Pull requests to `main` or `develop`

**Steps:**
- Validates PR title (semantic versioning)
- Auto-labels PR
- Warns on large PRs (>50 files)

## Required Secrets

Add these secrets in GitHub Settings → Secrets and variables → Actions:

### Backend Secrets
- `OPENAI_API_KEY` - Your OpenAI API key

### Deployment Secrets
- `RENDER_SERVICE_ID` - Your Render service ID
- `RENDER_API_KEY` - Your Render API key
- `VERCEL_DEPLOY_HOOK` - Vercel deploy hook URL

## How to Get Secrets

### Render Secrets
1. Go to https://dashboard.render.com/
2. Click on your service
3. Copy the Service ID from URL: `render.com/services/<SERVICE_ID>`
4. Go to Account Settings → API Keys
5. Create a new API key

### Vercel Deploy Hook
1. Go to https://vercel.com/dashboard
2. Select your project
3. Settings → Git → Deploy Hooks
4. Create a new hook and copy the URL

## Setting Up GitHub Secrets

```bash
# Go to your GitHub repository
# Settings → Secrets and variables → Actions → New repository secret

# Add each secret:
Name: OPENAI_API_KEY
Value: sk-proj-...

Name: RENDER_SERVICE_ID
Value: srv-...

Name: RENDER_API_KEY
Value: rnd_...

Name: VERCEL_DEPLOY_HOOK
Value: https://api.vercel.com/v1/integrations/deploy/...
```

## Branch Protection Rules

Recommended settings for `main` branch:

1. Go to Settings → Branches
2. Add branch protection rule for `main`
3. Enable:
   - ✅ Require a pull request before merging
   - ✅ Require status checks to pass before merging
     - Backend CI
     - Frontend CI
   - ✅ Require conversation resolution before merging
   - ✅ Do not allow bypassing the above settings

## Workflow Status Badges

Add to your README.md:

```markdown
![Backend CI](https://github.com/aabhas-mathur/AI-Gameshow/workflows/Backend%20CI/badge.svg)
![Frontend CI](https://github.com/aabhas-mathur/AI-Gameshow/workflows/Frontend%20CI/badge.svg)
![Deploy](https://github.com/aabhas-mathur/AI-Gameshow/workflows/Deploy/badge.svg)
```

## Local Testing

Test workflows locally with [act](https://github.com/nektos/act):

```bash
# Install act
brew install act  # macOS
# or
choco install act-cli  # Windows

# Run backend CI locally
act -j test -W .github/workflows/backend-ci.yml

# Run frontend CI locally
act -j test -W .github/workflows/frontend-ci.yml
```

## Troubleshooting

### Tests failing in CI but passing locally
- Check Python/Node.js versions match
- Ensure all dependencies are in requirements.txt/package.json
- Verify environment variables are set correctly

### Deployment not triggering
- Check if secrets are configured correctly
- Verify the service IDs and API keys
- Check workflow file syntax

### Coverage not uploading
- Ensure codecov token is set (optional)
- Check coverage.xml is generated
- Verify internet connectivity in CI

## Manual Deployment

If automatic deployment fails, deploy manually:

**Backend:**
```bash
# Trigger Render deployment via API
curl -X POST "https://api.render.com/v1/services/${RENDER_SERVICE_ID}/deploys" \
  -H "Authorization: Bearer ${RENDER_API_KEY}"
```

**Frontend:**
```bash
# Trigger Vercel deployment
curl -X POST "${VERCEL_DEPLOY_HOOK}"
```

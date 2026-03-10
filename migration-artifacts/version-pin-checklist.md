# Version Pin Checklist

## Files requiring version updates for migration

### UI Service (`ui/`)
- [ ] `ui/package.json` — React 18.2→19, Vite 4.3→6.x, all outdated deps
- [ ] `ui/vite.config.js` — Review for Vite 6 compatibility
- [ ] `ui/.eslintrc.cjs` — React version setting (`18.2` → `19`)
- [ ] `ui/Dockerfile` — Base image `node:18-alpine` → `node:22-alpine`

### Customer Auth Service (`customer-auth/`)
- [ ] `customer-auth/package.json` — All outdated deps (express, mongoose, nodemon, etc.)
- [ ] `customer-auth/Dockerfile` — Base image `node:14` → `node:22-slim`
- [ ] `customer-auth/.eslintrc.yml` — Review for ESLint compatibility

### ATM Locator Service (`atm-locator/`)
- [ ] `atm-locator/package.json` — All outdated deps (express, mongoose, nodemon, etc.)
- [ ] `atm-locator/Dockerfile` — Base image `node:14` → `node:22-slim`

### Python Services (accounts, transactions, loan, dashboard)
- [ ] `accounts/requirements.txt` — Pin all deps to latest stable versions
- [ ] `transactions/requirements.txt` — Pin all deps to latest stable versions
- [ ] `loan/requirements.txt` — Pin all deps to latest stable versions
- [ ] `dashboard/requirements.txt` — Pin all deps to latest stable versions
- [ ] `accounts/Dockerfile` — Base image `python` → `python:3.12-slim`
- [ ] `transactions/Dockerfile` — Base image `python` → `python:3.12-slim`
- [ ] `loan/Dockerfile` — Base image `python` → `python:3.12-slim`
- [ ] `dashboard/Dockerfile` — Base image `python` → `python:3.12-slim`

### Docker Compose
- [ ] `docker-compose.yaml` — Review for compatibility (no version pins to change, uses build contexts)

### CI/CD
- [ ] `.github/workflows/build_and_push_images.yml` — Update actions versions (checkout@v3→v4, etc.)

### Helm / Kubernetes
- [ ] `martianbank/values.yaml` — No version pins to change (uses image tags from GHCR)

### Performance Testing
- [ ] `performance_locust/requirements.txt` — Review for latest versions (out of scope per user request, but noted)

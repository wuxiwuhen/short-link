# Short Link Service 🔗

A URL shortener service built for practicing CI/CD workflows.

## Features

- 🔗 Create short URLs from long URLs
- 🔄 302 redirect to original URL
- 📊 Click tracking & statistics
- 🐳 Docker containerized
- 🚀 Full CI/CD pipeline with GitHub Actions

## Tech Stack

- **Backend:** Python 3.10+ / FastAPI
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **Container:** Docker multi-stage build
- **CI/CD:** GitHub Actions
- **Registry:** GitHub Container Registry (ghcr.io)

## Quick Start

### Local Development

```bash
# Install dependencies
make install

# Run in dev mode (hot reload)
make dev

# Run tests
make test

# Lint check
make lint
```

### Docker

```bash
# Build and run
make run

# Stop
make stop
```

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check |
| `POST` | `/api/shorten` | Create short URL |
| `GET` | `/{short_id}` | Redirect to original URL |
| `GET` | `/api/stats/{short_id}` | Get click statistics |

### Examples

```bash
# Create short URL
curl -X POST http://localhost:8000/api/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com/search?q=ci+cd+pipeline"}'

# Response
{"short_url":"/1","original_url":"https://www.google.com/search?q=ci+cd+pipeline"}

# Visit short URL → redirects to original
curl -L http://localhost:8000/1

# Check stats
curl http://localhost:8000/api/stats/1
# {"short_id":"1","original_url":"https://...","clicks":42}
```

## CI/CD Pipeline

### CI (Continuous Integration)

Triggered on every push to `main` and every Pull Request:

```
┌──────────────────────────────────────────┐
│             CI Pipeline                   │
├──────────┬──────────┬──────────┬─────────┤
│  Lint    │  Test    │ Security │ Docker  │
│  ruff    │  pytest  │pip-audit │ build   │
│  format  │  3.10/11 │  vuln    │ test    │
│          │  /12     │  scan    │         │
│          │  cov≥80% │          │         │
└──────────┴──────────┴──────────┴─────────┘
```

### CD (Continuous Deployment)

**Staging** — auto-deploy on merge to `main`:
- Builds Docker image → pushes to `ghcr.io`
- Tags: `staging` + `sha-<commit>`

**Production** — manual trigger with confirmation:
- Pulls staging image → retags as `production`
- Creates Git release tag
- Requires typing `DEPLOY` to confirm

## Project Structure

```
short-link/
├── .github/workflows/
│   ├── ci.yml                # PR + push: lint, test, security, docker
│   ├── cd-staging.yml        # main push → build & push image
│   └── cd-production.yml     # manual → promote staging to production
├── app/
│   ├── main.py               # FastAPI entry point
│   ├── routes.py             # API endpoints
│   ├── models.py             # SQLAlchemy models
│   ├── database.py           # DB config
│   └── utils.py              # Base62 encoder/decoder
├── tests/
│   ├── test_api.py           # API integration tests
│   └── test_utils.py         # Unit tests
├── Dockerfile                # Multi-stage Docker build
├── docker-compose.yml
├── requirements.txt
├── Makefile
└── README.md
```

## CI/CD Concepts Practiced

| Concept | How |
|---------|-----|
| Automated testing | pytest runs on every PR |
| Code quality gate | ruff lint + format check |
| Multi-version testing | Python 3.10, 3.11, 3.12 matrix |
| Coverage enforcement | Fail if coverage < 80% |
| Security scanning | pip-audit vulnerability check |
| Container build test | Docker build + health check in CI |
| Image registry | Push to GitHub Container Registry |
| Environment promotion | staging → production |
| Manual approval | Production requires `DEPLOY` confirmation |
| Automated tagging | Git tags created on production deploy |
# test branch protection

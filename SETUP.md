# Setup Guide

This project uses Docker to ensure consistent development across Mac, Linux, and Windows.

## Quick Start (All Platforms)

```bash
bash setup.sh
```

This will:
1. Clean up any old containers and volumes
2. Build fresh images
3. Start all services

## Manual Setup (if `setup.sh` doesn't work)

```bash
# Stop and remove everything
docker-compose down -v

# Start fresh
docker-compose up -d --build

# Check status
docker-compose ps
```

## Access Services

- **API Swagger UI**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5051
- **PostgreSQL**: localhost:5432 (user: daniel)
- **MongoDB**: localhost:27017 (user: datascientest)

## Troubleshooting

### Containers won't start
```bash
docker-compose down -v
docker-compose up -d --build
```

### Check logs
```bash
docker-compose logs -f api
docker-compose logs -f postgres
docker-compose logs -f mongodb
```

### Database issues
```bash
# Full reset
docker-compose down -v
rm -rf mongodata pgdata  # (these should be .gitignored anyway)
docker-compose up -d --build
```

## For Git Commits

Make sure these are never committed:
- `mongodata/` directory
- `pgdata/` directory
- `.env.local` file

The `.gitignore` already excludes these, but verify before committing.

## Important Notes

- **DO NOT** commit `mongodata/` or `pgdata/` directories
- **DO** commit `.env` with container names (no localhost)
- Always run `setup.sh` after pulling changes if database files were modified
- If one team member has issues, they should run `bash setup.sh` to get a fresh state

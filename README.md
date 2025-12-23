# FB Scheduler SaaS (Django + Next.js)

## Quick start (local)
1. Install Docker Desktop
2. From this folder:
```bash
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend:  http://localhost:8000/api
- Swagger:  http://localhost:8000/api/docs/

## Configure Facebook + AWS
Edit env values in `backend/.env.example` (or copy to `backend/.env` and update docker-compose to use it).
- Facebook: `FB_APP_ID`, `FB_APP_SECRET`, `FB_REDIRECT_URI`
- AWS: `AWS_S3_BUCKET_NAME`, `AWS_S3_REGION`, `AWS_S3_BASE_URL`, AWS credentials

## Notes
- Celery ETA scheduling is used for running publish tasks at the scheduled time.
- For production reliability you should run Redis + Postgres as managed services (ElastiCache + RDS) and run multiple workers.

## Docker Commands

- docker compose up -d --build
- docker compose down
- docker compose build --no-cache --pull backend
- docker compose up -d
- docker ps

// backend error check
- docker compose logs --tail=200 backend

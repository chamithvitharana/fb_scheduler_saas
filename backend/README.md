# Backend (Django + DRF + Celery)

## What it does
- Multi-tenant auth (JWT)
- Connect Facebook pages via OAuth
- Upload media to S3 via presigned URLs
- Schedule posts (text/link + optional media) and publish via Celery worker

## Run locally (Docker)
From repo root:

```bash
docker compose up --build
```

Backend API: http://localhost:8000/api  
Swagger docs: http://localhost:8000/api/docs/

## Configure Facebook
1. Create a Meta app (Facebook Login)
2. Add OAuth redirect URL:
   - `http://localhost:8000/api/facebook/callback/`
3. Set env vars in `docker-compose.yml` or `backend/.env`:
   - `FB_APP_ID`, `FB_APP_SECRET`, `FB_REDIRECT_URI`

## Configure AWS S3
Set:
- `AWS_S3_BUCKET_NAME`
- `AWS_S3_REGION`
- `AWS_S3_BASE_URL` (S3 or CloudFront)

Also configure AWS credentials in environment (or IAM role on ECS).

## Seed dev data
```bash
docker compose exec backend python manage.py seed_data
```

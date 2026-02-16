# Deploying BlinkChat API on Vercel

This folder is set up so you can deploy the Django API to Vercel. After deployment, **REST endpoints** (register, login, reports) work. **WebSockets do not** (Vercel serverless is request/response only), so **live chat matching and video will not work** unless you run the backend elsewhere (e.g. Railway, Render, or a VPS) with Daphne/ASGI.

## Required environment variables (Vercel dashboard)

Set these in your Vercel project → Settings → Environment Variables:

| Variable | Example | Required |
|--------|---------|----------|
| `ALLOWED_HOSTS` | `blink-chat-api.vercel.app` | Yes |
| `CORS_ORIGINS` | `https://your-frontend.vercel.app` | Yes (your UI URL) |
| `DJANGO_SECRET_KEY` | long random string | Yes |
| `JWT_SECRET` | long random string (or same as above) | Recommended |
| `DEBUG` | `False` | Recommended |

**Database:** Vercel’s filesystem is read-only, so SQLite will not work for registration/login. For a real deployment you need a hosted database (e.g. Vercel Postgres, Railway, or another provider) and must set `DATABASE_URL` (or configure `DATABASES` in settings) accordingly. Until then, only the public `GET /api/` health check will work.

## Deploy

1. In Vercel, create a project from your repo.
2. Set **Root Directory** to `api` (this folder).
3. Add the environment variables above.
4. Deploy.

## After deploy

- **GET** `https://blink-chat-api.vercel.app/api` or `https://blink-chat-api.vercel.app/api/` → should return `{"ok": true}`.
- **POST** `https://blink-chat-api.vercel.app/api/auth/register/` → register works.
- **WebSockets** (chat, video) → use a host that supports long-lived connections (e.g. Railway, Render) and point the frontend there for `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL`.

# BlinkChat – Post-deployment checklist

Use this to verify the app works after deploying the frontend (e.g. Vercel) and backend (e.g. VPS).

---

## 1. Set production env vars

**Frontend (Vercel)**  
- `NEXT_PUBLIC_API_URL` = your backend API base, e.g. `https://api.yourdomain.com/api`  
- `NEXT_PUBLIC_WS_URL` = your backend WebSocket URL, e.g. `wss://api.yourdomain.com` (optional; can be derived from API URL)

**Backend (VPS / host)**  
- `ALLOWED_HOSTS` = your API domain, e.g. `api.yourdomain.com`  
- `CORS_ORIGINS` = your frontend URL, e.g. `https://yourapp.vercel.app`  
- `DEBUG=False`  
- `REDIS_URL`, `MONGODB_URI` (or `MONGO_URI`), `DJANGO_SECRET_KEY` set correctly  

---

## 2. Check the frontend

| Step | What to do | Expected |
|------|------------|----------|
| 1 | Open your app URL (e.g. `https://yourapp.vercel.app`) | Landing page loads with “Start Chat”. |
| 2 | Click **Start Chat** | You go to `/chat` and see “Connecting…” then “Looking for someone…”. |
| 3 | Open the same chat URL in another tab/device | Two tabs should match; you see video + text chat. |

If the UI loads but chat never connects, the frontend is likely calling the wrong API/WebSocket URL → check `NEXT_PUBLIC_API_URL` and `NEXT_PUBLIC_WS_URL`.

---

## 3. Check the backend API

Replace `https://api.yourdomain.com` with your real backend URL.

| Step | What to do | Expected |
|------|------------|----------|
| 1 | **Health / root** | Open `https://api.yourdomain.com/` in browser | Django page or 404 (not 500). |
| 2 | **REST API** | `GET https://api.yourdomain.com/api/auth/register/` | `405 Method Not Allowed` (register only accepts POST). |
| 3 | **Register (optional)** | `POST https://api.yourdomain.com/api/auth/register/` with body `{"username":"testuser","password":"testpass123"}` | `201` and `{"user_id":..., "username":"testuser"}`. |

Use curl, Postman, or the browser Network tab when submitting the form.

```bash
# Example: test register
curl -X POST https://api.yourdomain.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

---

## 4. Check WebSockets

Chat and video need a working WebSocket to your backend.

| Step | What to do | Expected |
|------|------------|----------|
| 1 | Open DevTools → Network → filter “WS”. | When you click Start Chat, a request to `wss://api.yourdomain.com/ws/chat/` (or your `NEXT_PUBLIC_WS_URL`) appears. |
| 2 | Check status | WS request status **101** (Switching Protocols). |
| 3 | If **failed / red** | Backend or proxy is not accepting WebSockets; check Nginx/reverse proxy and that Daphne (or your ASGI server) is running. |

---

## 5. Common issues

| Symptom | Likely cause | Fix |
|--------|----------------|-----|
| Blank page or wrong API URL | Env not set or wrong at build time | Set `NEXT_PUBLIC_API_URL` (and `NEXT_PUBLIC_WS_URL`) in Vercel, redeploy. |
| “Connecting…” forever / no match | WebSocket not reaching backend | Ensure backend is on HTTPS and WSS; Nginx has `proxy_http_version 1.1`, `Upgrade`, `Connection "upgrade"`. |
| CORS errors in console | Frontend origin not allowed | Add exact frontend URL to backend `CORS_ORIGINS`. |
| 500 on API | Server error | Check backend logs (e.g. `journalctl -u your-app`, or host’s log dashboard). |
| Register/login 404 | Wrong path or backend not deployed | Confirm backend is deployed and path is `/api/auth/register/` (with trailing slash). |

---

## 6. Quick “smoke test” from your machine

```bash
# 1. Backend reachable
curl -I https://api.yourdomain.com/

# 2. Register works (replace URL)
curl -X POST https://api.yourdomain.com/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"smoketest","password":"test12345"}'
```

If both succeed and the frontend env points to this API (and WS) URL, you can then verify in the browser: open app → Start Chat → second tab → match and video/chat.

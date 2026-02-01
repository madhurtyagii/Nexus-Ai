# 🚀 Nexus AI Deployment Guide

This document contains the production configuration and credentials used for the Nexus AI deployment.

## 🔙 Backend (Render)
- **Service Name:** `nexus-ai-app-we26`
- **URL:** `https://nexus-ai-app-we26.onrender.com`
- **Region:** Singapore (`singapore`)
- **Runtime:** Python 3.11

### Essential Environment Variables
| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://postgres.wjqwxiwczojnqvnsjxbs:[PASSWORD]@aws-1-ap-southeast-1.pooler.supabase.com:6543/postgres` |
| `REDIS_URL` | Upstash Redis URL (provided in Render dashboard) |
| `ENV` | `production` |
| `CORS_ORIGINS` | `https://nexus-ai.vercel.app` (or your actual Vercel URL) |

---

## 🎨 Frontend (Vercel)
- **Framework:** Vite / React
- **Root Directory:** `frontend`

### Essential Environment Variables
| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | `https://nexus-ai-app-we26.onrender.com` |
| `VITE_WS_URL` | `wss://nexus-ai-app-we26.onrender.com/ws` |

---

## 🛠 Troubleshooting
1. **Migrations:** Database migrations run automatically via `migrate.py` on every deploy.
2. **Worker:** The custom task worker runs in the background of the web service to save on Render costs.
3. **Database:** Must use the **Supabase Transaction Pooler (Port 6543)** to work with Render's IPv4 network.

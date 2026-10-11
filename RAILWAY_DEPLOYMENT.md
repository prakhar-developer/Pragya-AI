# Railway Deployment Guide for PRAGYA AI

This repository is pre-configured for Railway deployment. You have two deployment options:

---

## 🌟 Option 1: 1-Click Unified Container (Recommended & Easiest)

Deploy both the FastAPI backend and React frontend together in a single container.
- **Benefits:** Single Railway service, 1 public URL, zero CORS setup needed, lowest cost.

### Steps:
1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Configure Railway deployment"
   git push origin main
   ```
2. **Log in to [Railway](https://railway.app)** and click **"New Project"**.
3. Select **"Deploy from GitHub repo"** and choose your `PRAGYA-AI-main` repository.
4. Railway will automatically detect the root `Dockerfile` and `railway.json`.
5. Go to the service **Variables** tab and add any optional credentials:
   - `GROQ_API_KEY` (optional, offline fallback enabled if blank)
   - `NEO4J_URI` (optional, in-memory graph enabled if blank)
   - `NEO4J_PASSWORD` (optional)
   - `SUPABASE_URL` (optional, in-memory store enabled if blank)
   - `SUPABASE_KEY` (optional)
6. Go to **Settings** -> **Networking** -> Click **"Generate Domain"** to get your public URL (e.g., `https://pragya-ai-production.up.railway.app`).
7. Open the generated domain in your browser!

---

## ⚡ Option 2: Two Separate Railway Services (Microservices)

If you prefer running Backend and Frontend as two independent services in Railway:

### Service 1: Backend (FastAPI)
1. In your Railway project, click **"+ New"** -> **"GitHub Repo"** -> select your repo.
2. In the service settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. In **Settings** -> **Networking**, generate a public domain (e.g. `https://pragya-backend.up.railway.app`).
4. In **Variables**, add:
   - `ALLOWED_ORIGINS` = `*` (or your frontend domain)
   - Any API keys (`GROQ_API_KEY`, `NEO4J_URI`, etc.)

### Service 2: Frontend (React / Vite)
1. In the same Railway project, click **"+ New"** -> **"GitHub Repo"** -> select the same repo.
2. In the service settings:
   - **Root Directory:** `frontend`
   - **Build Command:** `npm install && npm run build`
   - **Start Command:** `npx serve -s dist -l $PORT`
3. In **Variables**, add:
   - `VITE_API_BASE` = `https://pragya-backend.up.railway.app` (your backend service URL from Step 1)
4. In **Settings** -> **Networking**, generate a public domain for the frontend.

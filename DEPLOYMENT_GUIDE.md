# 🚀 Elevora - Production Deployment Guide

This guide walks you through deploying **Elevora (Resume Skill Gap Analyzer & ATS Career Intelligence Platform)** to production on any cloud platform of your choice.

---

## 🌟 Supported Deployment Platforms

| Platform | Best For | Database Supported | Deployment Time |
| :--- | :--- | :--- | :--- |
| **[Render](https://render.com)** *(Recommended)* | Full Web Service + Persistent DB | PostgreSQL, MySQL, SQLite | ~2 mins |
| **[Vercel](https://vercel.com)** | Serverless Python Functions | Neon Postgres, Supabase, SQLite | ~2 mins |
| **[Railway](https://railway.app)** | Instant Full-Stack Container | Managed PostgreSQL, MySQL | ~2 mins |
| **[Docker / VPS](https://docker.com)** | Self-Hosted Linux/Cloud Server | PostgreSQL (Compose), SQLite | ~1 min |

---

## 1. 🚀 Option 1: Deploy on Render (Recommended - Free & 24/7)

Render is the easiest way to deploy Python FastAPI applications with full background tasks and persistent database access.

### Step-by-Step Instructions:
1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Configure production deployment"
   git push origin main
   ```
2. Go to **[Render Dashboard](https://dashboard.render.com/)** and sign in with GitHub.
3. Click **New +** $ightarrow$ **Web Service**.
4. Select your `RESUME-SKILL-GAP-ANALYZER` repository.
5. Set the following settings:
   * **Name**: `elevora-resume-analyzer`
   * **Environment**: `Python`
   * **Region**: Choose closest to you (e.g., *Singapore*, *Frankfurt*, *Ohio*)
   * **Branch**: `main`
   * **Build Command**: `pip install -r requirements.txt`
   * **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   * **Plan**: `Free`
6. *(Optional - Database)*:
   * If you want a dedicated cloud database, create a **Free PostgreSQL** database on Render, copy its **Internal Database URL**, and add it as an Environment Variable named `DATABASE_URL`.
   * If omitted, Elevora will automatically run with zero-config SQLite!
7. Click **Deploy Web Service**. Your website will be live at `https://elevora-resume-analyzer.onrender.com`!

---

## 2. ⚡ Option 2: Deploy on Vercel (Serverless)

Elevora is fully configured with `vercel.json` and `api/index.py` for Vercel Serverless.

### Step-by-Step Instructions:
1. **Push your repository to GitHub**.
2. Go to **[Vercel Dashboard](https://vercel.com/new)** $ightarrow$ **Import Git Repository**.
3. Select your repository.
4. Set **Framework Preset**: `Other` (or leave default).
5. Under **Environment Variables**, add:
   * `SECRET_KEY`: `your-random-secret-key-string-12345`
   * *(Optional Database)* `DATABASE_URL`: Your free **Neon** or **Supabase** PostgreSQL URL (see section 5 below).
6. Click **Deploy**. Vercel will build and deploy your app in under 60 seconds!

---

## 3. 🚂 Option 3: Deploy on Railway

1. Go to **[Railway.app](https://railway.app)** $ightarrow$ **New Project**.
2. Select **Deploy from GitHub Repo**.
3. Click **+ Add Service** $ightarrow$ **Database** $ightarrow$ **Add PostgreSQL**.
4. Railway automatically injects `DATABASE_URL` into your web service.
5. Your application will build and deploy with full SSL!

---

## 4. 🐳 Option 4: Deploy with Docker & Docker Compose

For local production testing or deploying to any VPS (DigitalOcean, AWS EC2, Linode, Hetzner):

### Run with Docker Compose (Includes App + PostgreSQL Database):
```bash
docker-compose up -d --build
```
Your app will be running live at `http://localhost:8000` with connected PostgreSQL on port `5432`!

### Run Standalone Docker:
```bash
docker build -t elevora-app .
docker run -p 8000:8000 elevora-app
```

---

## 5. 🗄️ Free Cloud Databases Setup (Neon / Supabase / TiDB)

Elevora automatically works with any cloud database URL:

### A. Neon PostgreSQL (Free 0.5GB Serverless Postgres - Recommended)
1. Sign up at **[neon.tech](https://neon.tech)**.
2. Create a new project named `elevora_db`.
3. Copy the **Connection String** (e.g. `postgresql://user:pass@ep-xyz.aws.neon.tech/neondb?sslmode=require`).
4. Paste it as `DATABASE_URL` in your Vercel or Render Environment Variables.

### B. Supabase PostgreSQL (Free 500MB Postgres)
1. Sign up at **[supabase.com](https://supabase.com)**.
2. Create a new project $ightarrow$ Go to **Project Settings** $ightarrow$ **Database**.
3. Copy the **URI Connection String** (format: `postgresql://postgres:[PASSWORD]@db.xxxx.supabase.co:5432/postgres`).
4. Paste it as `DATABASE_URL` in your cloud host.

### C. TiDB Cloud (Free 5GB Serverless MySQL)
1. Sign up at **[tidbcloud.com](https://tidbcloud.com)**.
2. Create a free Serverless Cluster.
3. Copy the MySQL connection string and set it as `DATABASE_URL`.

---

## 🔒 Environment Variables Reference

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `PORT` | Web server port | `8000` (auto-assigned by cloud hosts) |
| `SECRET_KEY` | Key for session token signing | `resume-analyzer-secure-key-1234!` |
| `DATABASE_URL` | Universal DB connection URI | `postgresql://...` or `mysql://...` |
| `SMTP_HOST` | Email SMTP Host | `smtp.gmail.com` |
| `SMTP_PORT` | Email SMTP Port | `587` |
| `SMTP_USER` | Email sender address | `your-email@gmail.com` |
| `SMTP_PASSWORD`| Email App Password | *(Gmail 16-char App Password)* |

---

## 🧪 Health Check & Verification

Once deployed, visit your domain:
* **Live App**: `https://your-app-domain.com`
* **Health Check**: `https://your-app-domain.com/api/health`
* **API Documentation**: `https://your-app-domain.com/docs`

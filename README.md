# 🚗 Sakshi ALPR India • Enterprise Vehicle Intelligence

An enterprise-grade, decoupled Automatic License Plate Recognition (ALPR / ANPR) platform designed for **Indian Vehicles & High Security Registration Plates (HSRP)**.

Specialized for cars, bikes, scooters, trucks, and commercial vehicles with instant detection, OCR extraction, Indian state/RTO identification, and cloud database persistence to **Neon PostgreSQL**.

---

## 🏛️ Clean Architecture (2 Main Folders)

```
Sakshi_ALPR/
├── backend/                              # ⚙️ FASTAPI BACKEND & AI PIPELINE
│   ├── app/                              # Core logic, detector, OCR & RTO engine
│   │   ├── api/                          # REST API routes (detect, video, records, stats)
│   │   ├── core/                         # YOLOv8 detector, EasyOCR engine, postprocessor
│   │   └── database/                     # SQLAlchemy models & Neon PostgreSQL repository
│   ├── models/                           # Fine-tuned YOLOv8 model & EasyOCR weights
│   ├── data/                             # Storage directory & sample vehicles
│   ├── Dockerfile                        # Production Docker container definition
│   ├── .dockerignore
│   ├── .env.example                      # Configuration template
│   ├── requirements.txt                  # Python dependencies
│   └── run_backend.py                    # Local backend runner
│
├── frontend/                             # 💎 LIGHT MINIMAL WEB DASHBOARD
│   ├── public/
│   │   ├── index.html                    # Minimal light UI with authentic HSRP styling
│   │   └── app.js                        # Client API engine, live video & stream handlers
│   ├── Dockerfile                        # Production Docker container definition
│   ├── .dockerignore
│   ├── .env.example                      # Frontend environment template
│   ├── package.json
│   ├── requirements.txt                  # Lightweight Python server dependency
│   └── run_frontend.py                   # Frontend server with dynamic BACKEND_URL injection
│
├── docker-compose.yml                    # Multi-container local/cloud orchestration
├── run_backend.bat                       # One-click Windows backend launcher
├── run_frontend.bat                      # One-click Windows frontend launcher
└── run_all.bat                           # Launch both servers with 1 click
```

---

## 💡 Core Capabilities

1. **📁 Photo & Video Multi-Vehicle / Bike Detection**:
   - Upload traffic photos or full traffic videos (`.mp4`, `.avi`, `.mov`, `.mkv`).
   - Identifies all vehicles and bikes across frames.
   - Extracts unique plates with timestamp in video (e.g., `00:04`) and crops.
   - Automatically stores all identified unique plates into the cloud database.
2. **📸 Live Webcam Snapshot**:
   - Direct browser camera viewfinder with instant capture shutter.
3. **🎥 Real-Time Video Stream**:
   - Live stream with real-time bounding boxes, FPS monitor, and 10-second deduplication cache.
4. **📊 Cloud Database Records & Export**:
   - Full live table connected to **Neon PostgreSQL**.
   - Search by plate number, RTO district, or filter by state (`MH`, `DL`, `GJ`, `KA`, `UP`).
   - One-click CSV export and stored visual evidence modal.

---

## 🚀 How to Run Locally

### Option 1: One-Click Launcher (Windows)
Double-click:
👉 **`run_all.bat`**

This will automatically launch the **Backend (Port 8000)** and the **Frontend (Port 3000)** in two dedicated command windows and open your browser!

---

### Option 2: Using Docker Compose (Recommended for Any OS)
```bash
docker compose up --build
```
* **Frontend Web Dashboard:** `http://localhost:3000`
* **Backend API:** `http://localhost:8000`
* **Swagger API Documentation:** `http://localhost:8000/docs`

---

### Option 3: Manual Terminal Execution

#### 1. Start Backend:
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

pip install -r requirements.txt
python run_backend.py
```
* Server running at `http://localhost:8000`

#### 2. Start Frontend:
In a new terminal window:
```bash
cd frontend
pip install -r requirements.txt
python run_frontend.py
```
* Dashboard running at `http://localhost:3000`

---

## ☁️ Deployment Guide

### Deploying the Backend

The backend runs FastAPI with PyTorch and YOLOv8 in a Docker container.

#### 1. Deploy on Render
1. Create a new account on [Render](https://render.com).
2. Click **New +** -> **Web Service**.
3. Connect your GitHub repository (`https://github.com/ghanashyamauti/Sakshi_ALPR`).
4. Select **Docker** as the Runtime environment.
5. Set **Root Directory** to `backend`.
6. Add the following **Environment Variables**:
   - `DATABASE_URL`: Your Neon PostgreSQL connection string (`postgresql://user:password@ep-...neon.tech/neondb?sslmode=require`)
   - `PORT`: `8000`
   - `CORS_ORIGINS`: `["*"]`
7. Click **Create Web Service**. Render will build and deploy your backend automatically with a public URL (e.g., `https://sakshi-alpr-backend.onrender.com`).

#### 2. Deploy on Railway
1. Sign up on [Railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo**.
3. Select this repository, set root directory to `/backend`.
4. Under **Variables**, add `DATABASE_URL` with your Neon PostgreSQL URL.
5. Railway detects the `Dockerfile` automatically and provisions an endpoint.

---

### Deploying the Frontend

#### 1. Deploy on Vercel
1. Go to [Vercel](https://vercel.com) and click **Add New Project**.
2. Select your repository.
3. Set **Root Directory** to `frontend/public`.
4. Deploy as a static site.
5. In `frontend/public/app.js`, set `BACKEND_URL` to your live deployed backend URL (e.g. `https://sakshi-alpr-backend.onrender.com`).

#### 2. Deploy on Render (Static Site or Web Service)
1. On Render, click **New +** -> **Web Service**.
2. Connect this repository and set **Root Directory** to `frontend`.
3. Set Environment Variable:
   - `BACKEND_URL`: Your deployed backend URL (e.g., `https://sakshi-alpr-backend.onrender.com`).
4. Click **Deploy**.

---

## 🔒 Security Note
Never commit `.env` files containing live database passwords to public repositories. Always copy `.env.example` to `.env` for local development or configure secrets through your cloud provider's dashboard.

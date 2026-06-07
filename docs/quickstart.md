# Quickstart

## Local

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

```powershell
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Docker

```powershell
docker compose up --build
```

Open `http://127.0.0.1:5173`.

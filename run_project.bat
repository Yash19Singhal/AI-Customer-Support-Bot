@echo off
echo =========================================
echo 🚀 Starting AI Customer Support Bot
echo =========================================

IF NOT EXIST venv (
    echo 🔧 Creating virtual environment...
    python -m venv venv
    call venv\Scripts\activate
    pip install -r backend\requirements.txt
    python backend\db_init.py
) ELSE (
    echo ✅ Virtual environment already exists.
    call venv\Scripts\activate
)

echo ⚙️ Starting FastAPI backend...
start cmd /k "cd backend && uvicorn app:app --reload --port 8000"

timeout /t 3 >nul
echo 💬 Starting Streamlit frontend...
start cmd /k "cd frontend && streamlit run streamlit_app.py"

echo ✅ Project started. Visit:
echo Backend: http://127.0.0.1:8000
echo Frontend: http://localhost:8501
pause

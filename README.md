Installation & Setup
1️ Clone Repository
```
git clone https://github.com/<your-username>/ai-customer-support-bot.git
cd ai-customer-support-bot
```

2️ Setup Virtual Environment
```
python -m venv venv
source venv/bin/activate         
```
3️ Install Requirements
```
pip install -r backend/requirements.txt
```
4️ Initialize Database
```
python backend/db_init.py
```
5 Run Backend Server
```
cd backend
uvicorn app:app --reload --host 0.0.0.0 --port 8000

```
Backend runs at: http://localhost:8000

6 Run Frontend Chat UI
```
cd frontend
streamlit run streamlit_app.py
```

Frontend runs at: http://localhost:8501

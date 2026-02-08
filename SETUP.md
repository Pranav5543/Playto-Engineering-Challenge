# Setup Instructions

## Quick Start

1. **Copy environment files**:
   ```bash
   # Backend
   cd backend
   cp .env.sample .env
   
   # Frontend
   cd ../frontend
   cp .env.sample .env
   ```

2. **Install dependencies**:
   ```bash
   # Backend
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   
   # Frontend
   cd ../frontend
   npm install
   ```

3. **Run migrations and seed data**:
   ```bash
   cd backend
   python manage.py migrate
   python seed.py  # Optional: adds test data
   ```

4. **Start servers**:
   ```bash
   # Backend (Terminal 1)
   cd backend
   python manage.py runserver
   
   # Frontend (Terminal 2)
   cd frontend
   npm run dev
   ```

5. **Access the app**:
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000/api/

## Default Test Credentials

After running `seed.py`, you can login with:
- Username: `user1`
- Password: `pass123`

Or create a new account via the Register button.

## Running Tests

```bash
cd backend
python manage.py test feed.tests
```

All 13 tests should pass ✅

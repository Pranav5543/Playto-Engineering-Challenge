# Playto Community Feed

A high-performance prototype featuring threaded discussions and a dynamic dynamic leaderboard.

## Features
- **Post Feed**: Dynamic feed with likes and real-time interaction.
- **Threaded Comments**: Optimized nested discussions (N+1 query persistent).
- **24h Leaderboard**: Real-time karma calculation based on last 24h activity.
- **Premium UI**: Sleek dark mode design with glassmorphism and animations.

## Tech Stack
- **Backend**: Django, Django REST Framework, SQLite
- **Frontend**: React, Tailwind CSS, Framer Motion, Lucide React
- **Performance**: Single-query comment tree serialization.

## How to Run Locally

### Prerequisites
- Python 3.10+
- Node.js 20+ (Highly Recommended for Vite stability)

### Quick Start with Docker (Recommended)
```bash
docker-compose up --build
```

### Manual Setup
#### 1. Backend Setup
```bash
cd backend

# Copy environment file
cp .env.sample .env

python -m venv venv
.\venv\Scripts\activate  # Windows
# or: source venv/bin/activate # Unix
pip install -r requirements.txt
python manage.py migrate
python seed.py # Optional: Seeds the DB with test data
python manage.py runserver
```

### 2. Frontend Setup
```bash
cd frontend

# Copy environment file
cp .env.sample .env

npm install
npm run dev
```

## Default Test Credentials
After running `seed.py`:
- Username: `user1`
- Password: `pass123`

## Testing
- Verify the leaderboard by liking posts and checking the "Top Authors" widget.
- Verify threaded comments by nested replies.

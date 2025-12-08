# 🎬 Telegram Movie Bot

Professional Telegram bot for movie/video distribution with enterprise-grade architecture.

## Features

- 📥 **Movie Distribution** — Send movies by code
- 🔍 **Fuzzy Search** — Find movies by title
- 📺 **Series Support** — Multi-part movies/serials
- 📩 **User Requests** — Request movies from users
- 📢 **Broadcasting** — Send messages to all users with progress
- 💾 **Backup** — Auto/manual database backup
- 📊 **Statistics** — Detailed analytics
- 🔧 **Maintenance Mode** — Toggle bot availability
- 👥 **Admin Panel** — Full management interface

## Tech Stack

- **Python 3.11+** with async/await
- **aiogram 3.x** — Modern Telegram Bot framework
- **SQLAlchemy 2.0** — Async ORM
- **PostgreSQL** — Primary database
- **Redis** — Caching & rate limiting
- **Docker** — Containerized deployment

## Architecture

```
src/
├── bot/            # Presentation layer (handlers, keyboards, middlewares)
├── core/           # Configuration, exceptions, logging
├── infrastructure/ # Database, repositories, Unit of Work
└── texts/          # All messages in Uzbek
```

## Quick Start

### 1. Clone & Setup

```bash
git clone <repo>
cd movie-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # For development
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your settings
```

Required settings:
- `BOT_TOKEN` — Get from [@BotFather](https://t.me/BotFather)
- `PRIVATE_CHANNEL_ID` — Your private channel ID
- `SUPER_ADMIN_ID` — Your Telegram ID
- `DATABASE_URL` — PostgreSQL connection string

### 3. Run with Docker (Recommended)

```bash
# Start all services
make docker-up

# View logs
make docker-logs

# Stop
make docker-down
```

### 4. Run Locally (Development)

```bash
# Start PostgreSQL and Redis (or use Docker)
docker-compose -f docker/docker-compose.yml up -d postgres redis

# Run migrations
make migrate

# Start bot
make run-dev
```

## Commands

### User Commands
| Command | Description |
|---------|-------------|
| `/start` | Start bot |
| `/help` | Show help |
| `/search` | Search movies |
| `/request` | Request a movie |
| `/myrequest` | View your requests |
| `47` | Send movie by code |

### Admin Commands
| Command | Description |
|---------|-------------|
| `/admin` | Open admin panel |

## Development

```bash
# Run tests
make test

# Lint code
make lint

# Format code
make format

# Create migration
make migrate-new name="add_new_table"
```

## Project Structure

```
movie_bot/
├── src/
│   ├── bot/
│   │   ├── handlers/     # Message handlers
│   │   ├── keyboards/    # Inline keyboards
│   │   ├── middlewares/  # Request pipeline
│   │   ├── loader.py     # Bot instance
│   │   └── main.py       # Entry point
│   ├── core/
│   │   ├── config.py     # Settings
│   │   ├── constants.py  # Constants
│   │   ├── exceptions.py # Custom errors
│   │   └── logging.py    # Structured logs
│   ├── infrastructure/
│   │   ├── database/
│   │   │   ├── models/       # SQLAlchemy models
│   │   │   └── repositories/ # Data access
│   │   └── unit_of_work.py   # Transaction management
│   └── texts/
│       ├── messages.py   # All messages
│       └── buttons.py    # Button texts
├── docker/
├── tests/
├── Makefile
└── pyproject.toml
```

## License

MIT

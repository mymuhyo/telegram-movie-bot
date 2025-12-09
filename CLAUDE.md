# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Professional Telegram movie distribution bot built with Python 3.11+, aiogram 3.x, SQLAlchemy 2.0, PostgreSQL, and Redis. The bot distributes movies via unique codes, supports fuzzy search, handles series/multi-part content, and includes a comprehensive admin panel.

**Language**: All user-facing text is in Uzbek (src/texts/messages.py).

## Development Commands

### Setup
```bash
# Install dependencies
make install              # Production dependencies
make dev                  # Production + development dependencies

# Configure environment
cp .env.example .env      # Edit with your settings
```

### Running the Bot
```bash
# Local development
make run-dev              # Run with DEBUG=true

# Production
make run                  # Run bot

# Docker (recommended)
make docker-up            # Start all services (bot, postgres, redis)
make docker-down          # Stop all services
make docker-logs          # View bot logs
make docker-build         # Rebuild containers
```

### Database Migrations
```bash
make migrate              # Apply all pending migrations
make migrate-new name="description"  # Create new migration
make migrate-down         # Rollback last migration
```

### Testing & Quality
```bash
make test                 # Run all tests with coverage
make test-unit            # Run unit tests only
make test-integration     # Run integration tests only
make lint                 # Run ruff and mypy checks
make format               # Auto-format code with ruff
```

### Utilities
```bash
make clean                # Remove __pycache__ and cache directories
make backup               # Manual database backup
make create-admin id=123  # Create admin user by Telegram ID
```

## Architecture

### Layer Structure

```
src/
├── bot/                 # Presentation layer
│   ├── handlers/        # Command/message handlers (routers)
│   ├── keyboards/       # Inline keyboard builders
│   ├── middlewares/     # Request pipeline (auth, db, logging, throttling)
│   ├── loader.py        # Bot and dispatcher instances
│   └── main.py          # Entry point
├── core/                # Cross-cutting concerns
│   ├── config.py        # Pydantic settings from .env
│   ├── constants.py     # Application constants
│   ├── exceptions.py    # Custom exception classes
│   └── logging.py       # Structured logging (structlog)
├── infrastructure/      # Data access layer
│   ├── database/
│   │   ├── models/      # SQLAlchemy ORM models
│   │   ├── repositories/# Data access patterns
│   │   ├── base.py      # Base model with id/timestamps
│   │   └── session.py   # Async session factory
│   └── unit_of_work.py  # Transaction management pattern
└── texts/               # All Uzbek user messages
    ├── messages.py      # Bot responses
    └── buttons.py       # Button labels
```

### Key Architectural Patterns

**Unit of Work Pattern**
- All database operations use `UnitOfWork` for transaction management
- Injected via `DatabaseMiddleware` as `uow` in handler data
- Repositories accessed via `uow.movies`, `uow.users`, `uow.admins`, etc.
- Auto-commits on successful handler completion, auto-rollbacks on errors

**Repository Pattern**
- `BaseRepository`: Generic CRUD operations with async SQLAlchemy
- `SoftDeleteRepository`: Extends base with soft delete support (deleted_at)
- Repositories instantiated with AsyncSession in UnitOfWork context

**Middleware Pipeline** (in execution order):
1. `LoggingMiddleware` - Structured logging with request context
2. `DatabaseMiddleware` - UnitOfWork injection and transaction management
3. `UserMiddleware` - User creation/update, subscription checks, maintenance mode
4. `ThrottlingMiddleware` - Redis-based rate limiting

### Database Models

- **UserModel**: Telegram users (auto-created on first interaction)
- **MovieModel**: Movie metadata + Telegram file_id
- **SeriesModel**: Multi-part movies/series grouping
- **AdminModel**: Admin users with permissions
- **DownloadModel**: Download tracking for statistics
- **MovieRequestModel**: User movie requests with approval workflow
- **SettingModel**: Key-value bot settings
- **BroadcastModel**: Broadcast message tracking
- **AdminLogModel**: Admin action audit log

### Configuration

All settings in `src/core/config.py` loaded from `.env`:

**Required**:
- `BOT_TOKEN` - From @BotFather
- `PRIVATE_CHANNEL_ID` - Private channel for movie storage (must be negative int)
- `SUPER_ADMIN_ID` - Your Telegram user ID
- `DATABASE_URL` - PostgreSQL connection (use `postgresql+asyncpg://`)

**Optional**:
- `REDIS_URL` - Defaults to `redis://localhost:6379/0`
- `BACKUP_CHANNEL_ID` - Auto-backup destination
- `RATE_LIMIT_REQUESTS/SECONDS` - Throttling config
- `SEARCH_FUZZY_THRESHOLD` - Search sensitivity (0.0-1.0)

### Handler Registration

Handlers organized in two routers:
- `admin_router`: Admin panel handlers (in `src/bot/handlers/admin.py`, etc.)
- `user_router`: User-facing handlers (in `src/bot/handlers/user.py`, etc.)

Both registered in `src/bot/main.py:on_startup()`.

## Important Implementation Notes

### Alembic Migrations
- **Always** import all models in `alembic/env.py` for autogenerate
- Database URL automatically set from `settings.database_url` in env.py
- Use async engine configuration (already set up)

### Async/Await Patterns
- All database operations are async (use `await`)
- All aiogram handlers are async
- Use `async with uow as uow:` pattern for manual transactions
- UnitOfWork auto-commits via middleware; manual `await uow.commit()` only needed outside handlers

### Redis Integration
- Optional dependency (bot runs without it)
- Used for: rate limiting, movie search caching
- MovieRepository accepts optional Redis instance
- Check `if redis` before using in UnitOfWork

### Text Messages
- **Never hardcode messages** - all text in `src/texts/messages.py`
- Use `.format()` for dynamic values (e.g., `MOVIE_CARD.format(title=...)`)
- Keep Uzbek language consistency

### Testing
- Use `pytest-asyncio` for async test functions
- `tests/conftest.py` provides fixtures (async db session, etc.)
- Mock Telegram API calls in tests
- Coverage target: `src/` directory

## Common Development Tasks

### Adding a New Handler
1. Create handler function in appropriate file under `src/bot/handlers/`
2. Use `@router.message()` or `@router.callback_query()` decorators
3. Access UnitOfWork via `uow` parameter (injected by middleware)
4. Register router in `src/bot/main.py` if new file

### Adding a Database Model
1. Create model class in `src/infrastructure/database/models/`
2. Inherit from `Base` or existing models
3. Add to `__all__` in `models/__init__.py`
4. Create repository in `src/infrastructure/database/repositories/`
5. Add repository property to `UnitOfWork` class
6. Run `make migrate-new name="add_model_name"` for migration
7. Review and apply migration with `make migrate`

### Modifying Database Schema
1. Update model class definition
2. Generate migration: `make migrate-new name="description"`
3. Review generated migration in `alembic/versions/`
4. Apply: `make migrate`
5. Rollback if needed: `make migrate-down`

### Adding Bot Text
1. Add constant to `src/texts/messages.py`
2. Use `.format()` placeholders for dynamic content
3. Keep Uzbek language style consistent with existing messages

### Running Single Test
```bash
pytest tests/path/to/test_file.py::test_function_name -v
```

## Tech Stack Details

- **aiogram 3.x**: Modern Telegram Bot framework (fully async)
- **SQLAlchemy 2.0**: ORM with async support via asyncpg
- **Alembic**: Database migration tool
- **Redis**: Caching and rate limiting (optional)
- **RapidFuzz**: Fuzzy string matching for movie search
- **Structlog**: Structured JSON logging
- **Pydantic**: Settings validation and environment management
- **Pytest**: Testing with async and coverage support
- **Ruff**: Fast Python linter and formatter
- **Mypy**: Static type checking (strict mode enabled)

## Code Quality Standards

### Configured Tools
- **Ruff**: Line length 100, Python 3.11+ syntax
- **Mypy**: Strict mode enabled, ignore missing imports
- **Pytest**: Auto async mode, coverage for `src/`
- **Bandit**: Security checks (excluding tests)

### Type Hints
- Required for all function signatures
- Use `from typing import` for generic types
- SQLAlchemy types: `Sequence[Model]`, `Model | None`
- Async returns: `Awaitable[T]` or `Coroutine[Any, Any, T]`

## Docker Development

The project includes a complete Docker setup with PostgreSQL, Redis, and the bot.

### Local Development with Docker Services
```bash
# Start only database services for local bot development
docker compose -f docker/docker-compose.yml up -d postgres redis

# Run migrations
make migrate

# Start bot locally
make run-dev

# Stop services
docker compose -f docker/docker-compose.yml down
```

### Database GUI (Development)
```bash
# Start Adminer on http://localhost:8080
docker compose -f docker/docker-compose.yml --profile dev up adminer
```

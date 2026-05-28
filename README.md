# Map of Popular Locations

A Django REST Framework application for viewing and rating popular locations on an interactive map.

## Features
- **Authentication**: Session-based auth with registration and login.
- **Locations**: CRUD API with search and filtering by category and rating.
- **Popularity System**: Automated scoring based on ratings and review activity.
- **Reviews & Voting**: Leave reviews and vote (like/dislike) on them.
- **Subscriptions**: Subscribe to locations for email notifications on new reviews.
- **Export**: Export location data to CSV or JSON.

## Prerequisites
- Python 3.14+
- [Poetry](https://python-poetry.org/)
- [Docker](https://www.docker.com/) and Docker Compose

## Getting Started

### 1. Clone the repository
```bash
git clone <repository-url>
cd test-task
```

### 2. Environment Setup
Create a `.env` file in the root directory (refer to the project documentation for required variables):
```bash
cp .env.example .env  # If an example exists, otherwise create one manually
```

### 3. Install Dependencies
```bash
poetry install
```

### 4. Start Infrastructure
Run the database (PostgreSQL) and cache (Redis) using Docker:
```bash
docker-compose up -d
```

### 5. Run Migrations
```bash
poetry run python manage.py migrate
```

### 6. Start the Development Server
```bash
poetry run python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

## Running Tests
```bash
poetry run pytest
```

## Exporting Data
You can export locations via the API:
- CSV: `GET /api/locations/export/?format=csv`
- JSON: `GET /api/locations/export/?format=json`

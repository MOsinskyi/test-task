# Project GEMINI.md

## Project Overview
This is a Django 6.0 project named `test-task`. It is a fresh installation with a standard monolithic structure. The project uses **Poetry** for dependency management and includes a **Docker Compose** configuration for a PostgreSQL database.

### Main Technologies:
- **Framework:** Django 6.0
- **Language:** Python 3.14+
- **Dependency Management:** Poetry
- **Database:** PostgreSQL (via Docker) / SQLite (default in settings)
- **Testing:** pytest

## Building and Running

### Prerequisites
- Python 3.14 or higher
- [Poetry](https://python-poetry.org/docs/#installation)
- Docker and Docker Compose (optional, for PostgreSQL)

### Setup
1. **Install Dependencies:**
   ```bash
   poetry install
   ```
2. **Database (Optional):**
   The project is currently configured to use SQLite by default in `core/settings.py`. To use PostgreSQL, start the container:
   ```bash
   docker-compose up -d
   ```
   *Note: You will need to update `DATABASES` in `core/settings.py` to use the Postgres engine and provide credentials (referencing the `.env` file used by Docker).*

### Running the Application
```bash
python manage.py migrate
python manage.py runserver
```

### Testing
Run the test suite using `pytest`:
```bash
pytest
```

## Development Conventions
- **Project Structure:**
  - `core/`: Project configuration, settings, and root URLs.
  - `manage.py`: Django's command-line utility.
- **Settings:** Local development settings are in `core/settings.py`. Use environment variables for sensitive information (e.g., `SECRET_KEY`, database credentials).
- **Dependencies:** Always add new dependencies through `pyproject.toml` using `poetry add <package>`.
- **Coding Style:** Adhere to [PEP 8](https://peps.python.org/pep-0008/) and standard Django practices.

# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Generate passwords file (required before first run)
python mitasny/generate_passwords.py mitasny/passwords.py

# Initialize/migrate database
./manage.py migrate
./manage.py makemigrations tasks && ./manage.py migrate tasks

# Run all tests
./manage.py test

# Run tests for a specific app
./manage.py test tasks

# Run a single test module
./manage.py test tasks.tests.test_models

# Run development server
./manage.py runserver
```

## Architecture

Single Django app (`tasks`) with SQLite. The `mitasny/passwords.py` file holds `SECRET_KEY` and is gitignored — the project won't start without it.

### Models (`tasks/models.py`)

- **Project** — top-level container; `name` is a slug used in URLs. Computes `finish_date` and `total_work_left` across all tasks.
- **Task** — belongs to a Project; `work_left` (days) drives scheduling. `finish_date` is computed by accumulating `work_left` from preceding tasks (ordered by `order` field) plus its own, then calling `calculate_finish_date`.
- **Phase** — workflow state for tasks. The 7 required phases are `pending → ongoing → continuing → finished → done`, plus `blocked` and `impediment`. These must exist in the DB for the app to work correctly; tests create them via `ExtTestCase.create_default_phases()`.
- **Priority** — optional metadata on tasks.

### Business logic

- `tasks/calculate_finish_date.py` — pure function: given a start date and days-of-work, returns the finish date counting only Mon–Fri.
- `tasks/check_validity.py` — validates that the required Phase records exist in the DB.

### Views

Views are split by domain into three files, all using Django class-based views:
- `tasks/project.py` — Project CRUD + list + weekly report
- `tasks/task.py` — Task CRUD + move (reorder) + set-phase-to
- `tasks/tasks_user.py` — User registration, detail, edit, delete

### Tests

`tasks/tests/ext_test_case.py` provides `ExtTestCase` with two helpers used across all test files:
- `create_and_log_in_user()` — creates a user and authenticates the test client
- `create_default_phases()` — seeds the 7 required Phase records

### Deployment

Fabric (`deploy_tools/fabfile.py`) deploys to nginx + gunicorn. The gunicorn service is named after the site hostname (e.g., `local.mitasny.com.gunicorn`).

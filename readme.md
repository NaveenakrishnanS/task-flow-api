# Task Flow API

FastAPI + SQLAlchemy sample API for managing tasks, backed by SQLite.

Base URL: `/api/v1`

## Quick start (Windows PowerShell)

1) Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2) Install dependencies

```powershell
pip install -r requirements.txt
```

3) Run the API

```powershell
uvicorn main:app --reload
```

The server starts at: http://127.0.0.1:8000/api/v1

Open interactive docs: http://127.0.0.1:8000/docs

## Endpoints

- GET `/` – Health check
- POST `/tasks` – Create a task
- GET `/tasks` – List all tasks with optional pagination and filtering
  - Query parameters:
    - `skip` (optional, default: 0) – Number of tasks to skip for pagination
    - `limit` (optional, default: 100, max: 100) – Number of tasks to return
    - `status_filter` (optional) – Filter by status (e.g., "todo", "in_progress", "done")
    - `priority_filter` (optional) – Filter by priority (e.g., "low", "medium", "high")
    - `assignee_filter` (optional) – Filter by assignee name
  - Returns: `{"tasks": [...], "total": N, "skip": N, "limit": N}`
- GET `/tasks/{id}` – Get a single task by id
- PUT `/tasks/{id}` – Update a task (path contains id, body contains fields to change)
- DELETE `/tasks/{id}` – Delete a task by id

## Request/response models

- Pydantic models (API layer): `CreateTask`, `Task`, `UpdateTask`
- SQLAlchemy model (DB layer): `TaskTable`

The API converts between Pydantic and SQLAlchemy models under the hood.

### Enums

- `status`: `"todo" | "in_progress" | "done"`
- `priority`: `"low" | "medium" | "high"`
- `assignee`: defaults to `"unassigned"` if not provided

### Create task example

Note: `created_by` is required by the database model. Timestamps are set by the server.

```json
POST /api/v1/tasks
Content-Type: application/json

{
	"title": "Sample",
	"description": "optional description",
	"status": "todo",
	"priority": "low",
	"assignee": "unassigned",
	"created_by": "you",
	"due_date": "2025-12-31"
}
```

### Update task example

```json
PUT /api/v1/tasks
Content-Type: application/json

{
	"task_id": 1,
	"status": "in_progress",
	"priority": "high",
	"updated_by": "you"
}
```

## Database

- SQLite file: `db/database.db`
- Tables are created automatically on startup for development.

If you change columns and hit schema errors during development, stop the server and delete the database file to let it be recreated:

```powershell
Remove-Item -Path "db\database.db" -Force
```

For production, use Alembic migrations instead of auto-creating tables.

## Troubleshooting

- 500 with missing column: delete `db/database.db` and restart to recreate the schema.
- Enum binding error: ensure you send strings like `"todo"`, `"in_progress"`, `"done"` for enum fields.
- 204 delete response: endpoint returns no body by design.

## Next steps

- Add tests with pytest + FastAPI TestClient
- Add Alembic for schema migrations
- Move DB URL to environment variable (e.g., `DATABASE_URL`)

## Performance Optimizations

This project has been optimized for performance with:
- Database indexes on frequently queried columns
- Pagination support to handle large datasets efficiently
- Connection pooling for better resource management
- Optimized query patterns

See [PERFORMANCE_OPTIMIZATIONS.md](PERFORMANCE_OPTIMIZATIONS.md) for detailed information about the optimizations.


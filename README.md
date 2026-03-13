## Pydurma Critical Edition Backend

This project is a backend API for creating **Critical Editions** of texts from multiple **diplomatic versions**, built on top of the `Pydurma` library. It exposes HTTP endpoints so scholars can upload texts, run collations, and retrieve previous results without using the CLI.

### Tech Stack

- **Language**: Python
- **Framework**: FastAPI
- **ASGI Server**: Uvicorn
- **Database / ORM**: SQLAlchemy
- **Rate Limiting**: slowapi
- **Config & Utils**: python-dotenv, validators
- **Collation Engine**: Pydurma (via GitHub)

### Features (Planned / Implemented)

- **Upload diplomatic versions** of a text.
- **Run a collation** using Pydurma to generate a Critical Edition.
- **Store and retrieve** past collations.
- **REST API design** suitable for a future frontend.

### Setup

1. **Create and activate a virtual environment** (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
```

2. **Install dependencies**:

```bash
python -m pip install -r requirements.txt
```

3. **Run the development server** (adjust the module path if different):

```bash
uvicorn pydurma_app.main:app --reload
```

4. **Open API docs**:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Environment Variables

Create a `.env` file in the project root:

- **`ENV_NAME`**: `"Local"` to enable seeding
- **`BASE_URL`**: e.g. `http://127.0.0.1:8000`
- **`DB_URL`**: SQLAlchemy DB URL (PostgreSQL recommended)
- **`SECRET_KEY`**: JWT signing secret
- **`ALGORITHM`**: e.g. `HS256`
- **`TOKEN_EXPIRE_HOURS`**: token lifetime (hours)

### Authentication (JWT)

1. **Register**

- `POST /auth/register`

2. **Login**

- `POST /auth/login` → returns `{ "access_token": "...", "token_type": "bearer" }`

3. **Use the token**

Send the header:

- `Authorization: Bearer <access_token>`

In Swagger UI (`/docs`), click **Authorize** and paste `Bearer <access_token>`.

### Collation API

- **Create collation**
  - `POST /collate/`
  - Body: JSON array of strings (each string is a diplomatic version)
  - Success response includes `{ id, status, result }`
  - Failures are persisted with `status="failure"` and include trace/error details

- **History**
  - `GET /collate/history` → list of `{ id, status, created_at }`

- **Get one by id**
  - `GET /collate/{collation_id}` → full saved record (only if owned by JWT user)

### Project Goals

- Make Pydurma’s collation functionality accessible via a web API.
- Focus on backend logic and API structure (no frontend required).
- Keep the design simple but extensible for future features (rate limiting, advanced exports, etc.).


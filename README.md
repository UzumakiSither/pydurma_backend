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
pip install -r requirements.txt
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

- **Export collation**
  - `GET /collate/{collation_id}/download` -> download as file (only if owned by JWT user)

- **History**
  - `GET /collate/history` → list of `{ id, status, created_at, output_type }`

- **Get one by id**
  - `GET /collate/{collation_id}` → full saved record (only if owned by JWT user)

### Project Goals

- Make Pydurma’s collation functionality accessible via a web API.
- Focus on backend logic and API structure (no frontend required).
- Keep the design simple but extensible for future features (more exports type).

## Note

If you encounter issues cloning or installing the **pydurma** library on Windows due to file names that end with a space (which work on Linux-based systems but not on Windows), you can install and run the project using **WSL (Windows Subsystem for Linux)**.

```bash
# Install WSL
- Open windows powershell
wsl --install

# After installation, set your Linux username and password when prompted
# System restart might be required
# Open ubuntu

# Update the system
sudo apt update
sudo apt upgrade -y

# Install required tools
sudo apt install python3 python3-pip python3-venv git build-essential -y

# Verify installations
python3 --version
pip3 --version
git --version

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib

# If you encounter issues installing some Python dependencies, try this and then install the requirements again
pip install "setuptools<70"
pip install --no-build-isolation pyewts==0.2.0

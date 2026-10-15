"""Settings shared by every section's notebook."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# The Neon connection string lives in .env (git-ignored) under this name.
ENV_PATH = PROJECT_ROOT / ".env"
ENV_VAR_NAME = "NEON_DATABASE_URL"

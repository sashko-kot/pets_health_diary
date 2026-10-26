import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "pets_health.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"
QUERIES_PATH = BASE_DIR / "sql" / "queries.sql"


class ClosingConnection(sqlite3.Connection):
    """Commit or roll back on context exit, then close the connection."""

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()


def get_connection() -> sqlite3.Connection:
    """Open the project database with named rows and foreign keys enabled."""
    connection = sqlite3.connect(DB_PATH, factory=ClosingConnection)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database() -> None:
    """Create the schema if needed, using the project's SQL schema file."""
    with get_connection() as connection:
        connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_queries() -> dict[str, str]:
    """Read named SQL statements from queries.sql."""
    text = QUERIES_PATH.read_text(encoding="utf-8")
    queries = {}
    name = None
    statement = []
    for line in text.splitlines():
        if line.startswith("-- name: "):
            if name and statement:
                queries[name] = "\n".join(statement).strip()
            name = line.removeprefix("-- name: ").strip()
            statement = []
        elif name and not line.startswith("--"):
            statement.append(line)
    if name and statement:
        queries[name] = "\n".join(statement).strip()
    return queries

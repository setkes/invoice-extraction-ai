import os
from sqlmodel import create_engine, Session
from dotenv import load_dotenv

load_dotenv()

# Builds the DB connection URL in the format understood by SQLAlchemy:
# postgresql://user:password@host/db_name
DATABASE_URL = (
    f"postgresql://{os.getenv('POSTGRES_USER', 'invoice_user')}"
    f":{os.getenv('POSTGRES_PASSWORD', 'password123')}"
    f"@{os.getenv('POSTGRES_HOST', 'localhost')}"
    f"/{os.getenv('POSTGRES_DB', 'invoice_db')}"
)

# The engine is the master DB connection. We create one per application.
# echo=False means it won't print every SQL query to the terminal.
engine = create_engine(DATABASE_URL, echo=False)


def get_session():
    """
    Returns a SQLModel Session.
    The Session acts like a "cart": it accumulates operations
    (insert, update, delete) and sends them all to the DB together on .commit().
    FastAPI uses it as a dependency via Depends(get_session).
    """
    with Session(engine) as session:
        yield session

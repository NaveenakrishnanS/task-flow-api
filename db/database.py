from db.model.db_model import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sqlite_filename = "db/database.db"
sqlite_url = f"sqlite:///{sqlite_filename}"
connect_args = {"check_same_thread": False}

# Configure connection pool for better resource management
# pool_pre_ping ensures connections are alive before using them
# pool_size and max_overflow control the connection pool size
engine = create_engine(
    sqlite_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=5,  # Number of connections to maintain in the pool
    max_overflow=10,  # Additional connections when pool is exhausted
    echo=False  # Set to True for SQL query logging during development
)

SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


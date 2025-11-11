from db.model.db_model import Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sqlite_filename = "db/database.db"
sqlite_url = f"sqlite:///{sqlite_filename}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url,connect_args=connect_args)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


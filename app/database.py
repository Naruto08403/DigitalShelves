from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./digitalShelves.db"  # Change to your preferred DB

engine = create_engine(SQLALCHEMY_DATABASE_URL, 
                       connect_args={"check_same_thread": False},pool_size=10,           # Set a higher pool size
    max_overflow=20,        # Allow more connections to overflow beyond pool_size
    pool_timeout=60,        # Optional: Increase the timeout
    pool_recycle=1800 )      # Optional: Recycle connections after 30 minutes)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

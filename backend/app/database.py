import os
import time

from sqlmodel import Session, create_engine


DATABASE_URL = (
    f"mysql+pymysql://"
    f"{os.getenv('MYSQL_USER')}:"
    f"{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST', 'mysql')}:"
    f"{os.getenv('MYSQL_PORT', '3306')}/"
    f"{os.getenv('MYSQL_DATABASE')}"
)

engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)


def wait_for_database():
    while True:
        try:
            with engine.connect():
                print("Connected to MySQL")
                break
        except Exception:
            print("Waiting for MySQL...")
            time.sleep(2)


def get_session():
    with Session(engine) as session:
        yield session
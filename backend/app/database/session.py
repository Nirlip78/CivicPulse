from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from backend.app.core.config import DATABASE_URL

engine_args = {"connect_args": {"check_same_thread": False}} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, **engine_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def migrate_schema():
    Base.metadata.create_all(bind=engine)
    if not DATABASE_URL.startswith("sqlite"):
        return
    expected = {"reference":"VARCHAR(40)","title":"VARCHAR(180)","preferred_language":"VARCHAR(40)","detected_language":"VARCHAR(80)","original_location":"VARCHAR(255)","locality":"VARCHAR(120)","landmark":"VARCHAR(255)","geocoded_address":"VARCHAR(500)","location_source":"VARCHAR(30)","latitude":"FLOAT","longitude":"FLOAT","supporting_information":"TEXT","intent":"VARCHAR(50)","priority":"VARCHAR(20) DEFAULT 'Normal'","resolved_at":"DATETIME"}
    with engine.begin() as connection:
        existing = {item["name"] for item in inspect(connection).get_columns("complaints")}
        for name, definition in expected.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE complaints ADD COLUMN {name} {definition}"))

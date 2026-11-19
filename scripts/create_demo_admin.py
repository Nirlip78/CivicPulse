"""Create an explicit local demo administrator; never run automatically."""
import os
import sys
from backend.app.core.security import hash_password
from backend.app.database.session import Base, SessionLocal, engine
from backend.app.models import User

email=os.getenv("DEMO_ADMIN_EMAIL")
password=os.getenv("DEMO_ADMIN_PASSWORD")
if not email or not password or len(password)<10:
    sys.exit("Set DEMO_ADMIN_EMAIL and DEMO_ADMIN_PASSWORD (minimum 10 characters).")
Base.metadata.create_all(bind=engine)
db=SessionLocal()
try:
    user=db.query(User).filter_by(email=email.lower()).first()
    if user: user.role="admin"
    else: db.add(User(email=email.lower(),password_hash=hash_password(password),role="admin"))
    db.commit(); print(f"Demo administrator ready: {email}")
finally: db.close()

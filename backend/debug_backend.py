from app import models, database, auth
from sqlalchemy.orm import Session
import os

print("Creating tables...")
try:
    models.Base.metadata.create_all(bind=database.engine)
    print("Tables created.")
except Exception as e:
    print(f"Table Creation Error: {e}")

print("Hashing password...")
try:
    h = auth.get_password_hash("test")
    print(f"Hashed: {h}")
except Exception as e:
    print(f"Hashing Error: {e}")

print("Creating User...")
db = database.SessionLocal()
try:
    # Cleanup previous debug run
    old = db.query(models.User).filter(models.User.email == "debug@test.com").first()
    if old:
        db.delete(old)
        db.commit()
        
    u = models.User(email="debug@test.com", hashed_password=h, is_admin=True)
    db.add(u)
    db.commit()
    print("User created.")
except Exception as e:
    print(f"DB Error: {e}")
finally:
    db.close()

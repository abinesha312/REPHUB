#!/usr/bin/env python
"""
Initialize the database with pgvector extension and create tables.
Run this script to set up the database before first use.
"""
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from app.database import init_db
from app.models import User

print("Initializing database...")

try:
    init_db()
    print("✓ Database initialized successfully")
    print("✓ pgvector extension enabled")
    print("✓ Tables created")
    
    # Create a default user
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.id == 1).first()
        if not existing_user:
            default_user = User(id=1, username="default_user", email="user@example.com")
            db.add(default_user)
            db.commit()
            print("✓ Default user created (id=1)")
        else:
            print("✓ Default user already exists")
    finally:
        db.close()
    
    print("\nDatabase ready! You can now start the application.")
    
except Exception as e:
    print(f"✗ Error initializing database: {e}")
    sys.exit(1)

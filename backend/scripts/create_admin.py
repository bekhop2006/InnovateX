"""
Script to create the first admin user.
"""
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy.orm import Session
from models.user import User, UserRole
from services.auth.service import hash_password
from database import SessionLocal


def create_first_admin(
    email: str = "admin@innovatex.com",
    password: str = "admin123",
    name: str = "Admin",
    surname: str = "InnovateX"
):
    """
    Create the first admin user.
    
    Args:
        email: Admin email
        password: Admin password
        name: Admin first name
        surname: Admin surname
    """
    db: Session = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == email).first()
        
        if existing_admin:
            print(f"⚠️  Admin user with email {email} already exists!")
            print(f"   User ID: {existing_admin.id}")
            print(f"   Name: {existing_admin.name}")
            print(f"   Role: {existing_admin.role.value}")
            return
        
        # Create admin user
        admin = User(
            name=name,
            surname=surname,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.admin
        )
        
        db.add(admin)
        db.commit()
        db.refresh(admin)
        
        print("✅ Admin user created successfully!")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Name: {name} {surname}")
        print(f"   Role: {admin.role.value}")
        print(f"\n⚠️  IMPORTANT: Please change the default password after first login!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating admin user: {e}")
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--email", default="admin@innovatex.com", help="Admin email")
    parser.add_argument("--password", default="admin123", help="Admin password")
    parser.add_argument("--name", default="Admin", help="Admin first name")
    parser.add_argument("--surname", default="InnovateX", help="Admin surname")
    
    args = parser.parse_args()
    
    create_first_admin(
        email=args.email,
        password=args.password,
        name=args.name,
        surname=args.surname
    )


"""
Script to create the initial admin user.

This script creates the first admin user for the GazTracker application.
Run this script inside the backend container.

Usage:
    docker exec -it gaztracker_backend python scripts/create_admin.py
"""

import asyncio
import sys
from pathlib import Path

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import db_manager
from app.models.user import User, UserRole
from app.utils.security import hash_password


async def create_admin_user():
    """Create the initial admin user."""

    # Admin user details
    admin_email = "admin@gaztracker.com"
    admin_password = "admin123"  # Change this after first login!

    # Ensure database is initialized
    if not db_manager.async_session_maker:
        db_manager.init_db()

    async with db_manager.async_session_maker() as session:
        # Check if admin already exists
        from sqlalchemy import select
        result = await session.execute(
            select(User).where(User.email == admin_email)
        )
        existing_admin = result.scalar_one_or_none()

        if existing_admin:
            print(f"❌ Admin user already exists: {admin_email}")
            print(f"   User ID: {existing_admin.id}")
            print(f"   Role: {existing_admin.role}")
            return

        # Create admin user
        admin_user = User(
            email=admin_email,
            password_hash=hash_password(admin_password),
            first_name="System",
            last_name="Administrator",
            role=UserRole.ADMIN,
            phone_number="+33123456789",
            is_active=True,
            is_verified=True
        )

        session.add(admin_user)
        await session.commit()
        await session.refresh(admin_user)

        print("✅ Admin user created successfully!")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   User ID: {admin_user.id}")
        print(f"   Role: {admin_user.role}")
        print("\n⚠️  IMPORTANT: Change the password after first login!")


if __name__ == "__main__":
    asyncio.run(create_admin_user())

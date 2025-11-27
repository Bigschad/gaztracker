"""
Script to create test users for mobile app testing.

This script creates test users with different roles for testing the GazTracker mobile application.
Run this script inside the backend container.

Usage:
    docker exec -it gaztracker_backend python scripts/create_test_users.py
"""

import asyncio
import sys
from pathlib import Path

# Add app to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import db_manager
from app.models.user import User, UserRole
from app.utils.security import hash_password


async def create_test_users():
    """Create test users with different roles for mobile app testing."""

    # Test users with different roles
    test_users = [
        {
            "email": "admin@gaztracker.com",
            "password": "admin123",
            "first_name": "System",
            "last_name": "Administrator",
            "role": UserRole.ADMIN,
            "phone_number": "+33123456789",
        },
        {
            "email": "chauffeur@test.com",
            "password": "test123",
            "first_name": "Jean",
            "last_name": "Dupont",
            "role": UserRole.CHAUFFEUR,
            "phone_number": "+33612345678",
        },
        {
            "email": "operateur@test.com",
            "password": "test123",
            "first_name": "Marie",
            "last_name": "Martin",
            "role": UserRole.OPERATEUR_USINE,
            "phone_number": "+33612345679",
        },
        {
            "email": "responsable@test.com",
            "password": "test123",
            "first_name": "Pierre",
            "last_name": "Bernard",
            "role": UserRole.RESPONSABLE_LOGISTIQUE,
            "phone_number": "+33612345680",
        },
    ]

    # Ensure database is initialized
    if not db_manager.async_session_maker:
        db_manager.init_db()

    async with db_manager.async_session_maker() as session:
        created_count = 0
        existing_count = 0

        for user_data in test_users:
            # Check if user already exists
            result = await session.execute(
                select(User).where(User.email == user_data["email"])
            )
            existing_user = result.scalar_one_or_none()

            if existing_user:
                print(f"⚠️  User already exists: {user_data['email']} (Role: {existing_user.role})")
                existing_count += 1
                continue

            # Create user
            user = User(
                email=user_data["email"],
                password_hash=hash_password(user_data["password"]),
                first_name=user_data["first_name"],
                last_name=user_data["last_name"],
                role=user_data["role"],
                phone_number=user_data["phone_number"],
                is_active=True,
                is_verified=True,
            )

            session.add(user)
            await session.commit()
            await session.refresh(user)

            print(f"✅ Created user: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Role: {user_data['role']}")
            print(f"   User ID: {user.id}\n")
            created_count += 1

        print("=" * 60)
        print(f"Summary: {created_count} users created, {existing_count} already existed")
        print("=" * 60)
        print("\n📱 Comptes de test pour l'application mobile:\n")
        print("┌─────────────────────────────┬──────────────┬─────────────────────────────┐")
        print("│ Email                       │ Password     │ Role                        │")
        print("├─────────────────────────────┼──────────────┼─────────────────────────────┤")
        for user_data in test_users:
            role_display = user_data["role"].value
            print(f"│ {user_data['email']:<27} │ {user_data['password']:<12} │ {role_display:<27} │")
        print("└─────────────────────────────┴──────────────┴─────────────────────────────┘")
        print("\n⚠️  IMPORTANT: Change passwords in production!")


if __name__ == "__main__":
    asyncio.run(create_test_users())


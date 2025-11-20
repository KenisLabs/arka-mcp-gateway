"""
Update admin user email and password.

This script allows you to update the admin user's credentials in the database.
It will hash the password using bcrypt before storing it.

Usage:
    python -m utils.update_admin --email new@example.com --password newpassword123

Or run interactively:
    python -m utils.update_admin
"""
import asyncio
import argparse
from getpass import getpass
from sqlalchemy import select, update
from database import get_db_session
from gateway.models import User
import bcrypt
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def update_admin_user(email: str = None, password: str = None):
    """
    Update admin user credentials.

    Args:
        email: New email address (optional)
        password: New password (optional)
    """
    async with get_db_session() as db:
        # Find the admin user
        result = await db.execute(
            select(User).where(User.role == "admin")
        )
        admin_user = result.scalar_one_or_none()

        if not admin_user:
            logger.error("❌ No admin user found in database!")
            return

        logger.info(f"📝 Found admin user: {admin_user.email}")

        # Update email if provided
        if email:
            old_email = admin_user.email
            admin_user.email = email
            logger.info(f"✓ Email updated: {old_email} → {email}")

        # Update password if provided
        if password:
            hashed_password = hash_password(password)
            admin_user.password_hash = hashed_password
            logger.info("✓ Password updated (hashed with bcrypt)")

        # Commit changes
        await db.commit()

        logger.info("\n" + "="*60)
        logger.info("✓ Admin user updated successfully!")
        logger.info("="*60)
        logger.info(f"Email: {admin_user.email}")
        logger.info(f"Role: {admin_user.role}")
        logger.info("="*60)


async def main():
    """Main function to handle command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Update admin user email and password"
    )
    parser.add_argument(
        "--email",
        help="New email address for admin user",
        default=None
    )
    parser.add_argument(
        "--password",
        help="New password for admin user",
        default=None
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Interactive mode (prompts for inputs)"
    )

    args = parser.parse_args()

    email = args.email
    password = args.password

    # Interactive mode
    if args.interactive or (not email and not password):
        logger.info("Interactive mode - press Enter to skip a field\n")

        email_input = input("New email (leave empty to skip): ").strip()
        if email_input:
            email = email_input

        password_input = getpass("New password (leave empty to skip): ").strip()
        if password_input:
            password_confirm = getpass("Confirm password: ").strip()
            if password_input != password_confirm:
                logger.error("❌ Passwords do not match!")
                return
            password = password_input

    # Check if at least one field is being updated
    if not email and not password:
        logger.warning("⚠️  No updates specified. Exiting.")
        return

    # Confirm changes
    logger.info("\nYou are about to update:")
    if email:
        logger.info(f"  - Email: {email}")
    if password:
        logger.info(f"  - Password: {'*' * len(password)}")

    confirm = input("\nProceed? (yes/no): ").strip().lower()
    if confirm not in ["yes", "y"]:
        logger.info("Cancelled.")
        return

    # Update admin user
    await update_admin_user(email=email, password=password)


if __name__ == "__main__":
    asyncio.run(main())

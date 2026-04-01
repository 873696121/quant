"""Authentication service."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.schemas.user import UserCreate, TokenResponse, UserResponse


class AuthService:
    """Service for authentication operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, user_data: UserCreate) -> User:
        """Register a new user."""
        # Check if username exists
        result = await self.db.execute(
            select(User).where(User.username == user_data.username)
        )
        if result.scalar_one_or_none():
            raise ValueError("Username already exists")

        # Create user
        user = User(
            username=user_data.username,
            password_hash=hash_password(user_data.password),
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def authenticate(self, username: str, password: str) -> User:
        """Authenticate a user."""
        result = await self.db.execute(
            select(User).where(User.username == username)
        )
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise ValueError("Invalid username or password")

        return user

    def create_token(self, user: User) -> TokenResponse:
        """Create access token for user."""
        token = create_access_token(user.id)
        return TokenResponse(
            access_token=token,
            user=UserResponse.model_validate(user),
        )

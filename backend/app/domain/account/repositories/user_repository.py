from typing import Optional
from app.domain.account.aggregates.user import User


class UserRepository:
    """用户仓储接口"""

    async def find_by_id(self, user_id: int) -> Optional[User]:
        raise NotImplementedError

    async def find_by_username(self, username: str) -> Optional[User]:
        raise NotImplementedError

    async def save(self, user: User) -> User:
        raise NotImplementedError

    async def delete(self, user_id: int) -> None:
        raise NotImplementedError

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    """用户聚合根"""
    id: Optional[int] = None
    username: str = ""
    password_hash: str = ""
    qmt_account: str = ""
    qmt_password: str = ""
    qmt_server: str = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def update_qmt_credentials(
        self,
        account: str,
        password: str,
        server: str
    ) -> None:
        """更新QMT凭证"""
        self.qmt_account = account
        self.qmt_password = password
        self.qmt_server = server
        self.updated_at = datetime.now()

    def clear_qmt_credentials(self) -> None:
        """清除QMT凭证"""
        self.qmt_account = ""
        self.qmt_password = ""
        self.qmt_server = ""
        self.updated_at = datetime.now()

    def has_qmt_credentials(self) -> bool:
        """是否有QMT配置"""
        return bool(self.qmt_account and self.qmt_password)

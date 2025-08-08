from dataclasses import dataclass

from domain.email import Email
from domain.member_id import MemberId


@dataclass
class Member:
    id: MemberId
    nickname: str
    attendance_count: int = 0
    email: Email

    def record_attendance(self) -> None:
        self.attendance_count += 1

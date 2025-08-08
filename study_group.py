from dataclasses import dataclass, field

from .email import Email
from .member import Member
from .member_id import MemberId
from .study_group_id import StudyGroupId
from .study_group_state import StudyGroupState


@dataclass
class StudyGroup:
    id: StudyGroupId
    leader_id: MemberId
    max_members: int
    state: StudyGroupState
    _members: list[Member] = field(init=False, default_factory=list)

    @property
    def members(self) -> list[Member]:
        """멤버 리스트의 복사본을 반환하여 외부에서의 직접적인 수정을 방지합니다."""
        return self._members.copy()

    @classmethod
    def create(
        cls, leader_nickname: str, leader_email: str, max_members: int
    ) -> "StudyGroup":
        """스터디 그룹을 생성하고, 생성자를 첫 멤버이자 리더로 설정합니다."""
        if max_members < 2:
            raise ValueError("스터디 그룹 최소 인원은 2명 이상이어야 합니다.")

        leader_id = MemberId()
        leader = Member(
            id=leader_id, nickname=leader_nickname, email=Email(leader_email)
        )

        new_group = cls(
            id=StudyGroupId(),
            leader_id=leader_id,
            max_members=max_members,
            state=StudyGroupState.RECRUITING,
        )

        new_group._members.append(leader)

        return new_group

    def add_member(self, member: Member) -> None:
        if self.state != StudyGroupState.RECRUITING:
            raise ValueError("모집중인 스터디에만 참여할 수 있습니다.")
        if len(self._members) >= self.max_members:
            raise ValueError("스터디 그룹 정원을 초과하였습니다.")
        if any(m.id == member.id for m in self._members):
            raise ValueError("이미 참여하고 있는 멤버입니다.")

        self._members.append(member)

    def expel_member(self, member_id: MemberId) -> None:
        if member_id == self.leader_id:
            raise ValueError("스터디 그룹장은 내보낼 수 없습니다.")

        member_to_remove = next((m for m in self._members if m.id == member_id), None)
        if not member_to_remove:
            raise ValueError("존재하지 않는 멤버입니다.")

        self._members.remove(member_to_remove)

    def start_study(self) -> None:
        if self.state != StudyGroupState.RECRUITING:
            raise ValueError("모집중인 스터디만 시작할 수 있습니다.")
        if len(self._members) < 2:
            raise ValueError("스터디를 시작하기에 인원이 부족합니다. (최소 2명)")

        self.state = StudyGroupState.IN_PROGRESS

    def end_study(self) -> None:
        self.state = StudyGroupState.ENDED

    def record_attendance(self, member_id: MemberId) -> None:
        if self.state != StudyGroupState.IN_PROGRESS:
            raise ValueError("진행중인 스터디에서만 출석을 기록할 수 있습니다.")

        member = next((m for m in self._members if m.id == member_id), None)
        if member is None:
            raise ValueError("존재하지 않는 멤버입니다.")

        member.record_attendance()

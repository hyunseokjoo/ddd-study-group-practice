from enum import Enum, auto


class StudyGroupState(Enum):
    """스터디 그룹 상태를 나타내는 Value Object(불변으로 작성)"""

    RECRUITING = auto()
    IN_PROGRESS = auto()
    ENDED = auto()

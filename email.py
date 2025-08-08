from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Email:
    """
    이메일을 나타내는 불변(immutable) 값 객체(Value Object).
    - frozen=True: 불변성을 보장합니다.
    - __post_init__: 생성자 호출 후 값의 유효성을 검사합니다.
    """

    value: str

    def __post_init__(self):
        # 정규식을 사용하여 이메일 형식의 유효성을 검사합니다.
        if not re.match(
            r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", self.value
        ):
            raise ValueError("유효하지 않은 이메일 주소 형식입니다.")

    def __str__(self) -> str:
        return self.value

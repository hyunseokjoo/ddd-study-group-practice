from dataclasses import dataclass, field
import uuid


@dataclass(frozen=True)
class MemberId:
    value: uuid.UUID = field(default_factory=uuid.uuid4)

    def __str__(self):
        return str(self.value)

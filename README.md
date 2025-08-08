## 스터디 그룹 관리 도메인 모델 (DDD 연습)

이 프로젝트는 도메인 주도 설계(DDD)의 핵심 개념을 적용하여 '스터디 그룹'이라는 특정 도메인을 모델링하는 연습입니다. 애그리거트, 엔티티, 값 객체의 역할을 명확히 구분하고, 객체가 자신의 비즈니스 규칙(일관성)을 스스로 지키도록 설계하는 데 중점을 두었습니다.
도메인 모델 다이어그램
아래 다이어그램은 스터디 그룹 도메인의 핵심 구성요소와 그 관계를 보여줍니다.

'''mermaid
classDiagram
    direction LR
    class StudyGroup {
        <<AggregateRoot>>
        -id: StudyGroupId
        -leader_id: MemberId
        -max_members: int
        -state: StudyGroupState
        -_members: List~Member~
        +members() List~Member~
        +create(leader_info) StudyGroup
        +add_member(member_info)
        +expel_member(memberId)
        +start_study()
    }

    class Member {
        <<Entity>>
        +id: MemberId
        +nickname: str
        +email: Email
        +attendance_count: int
    }

    class StudyGroupId {
      <<ValueObject>>
      +value: UUID
    }
    class MemberId {
      <<ValueObject>>
      +value: UUID
    }
    class Email {
      <<ValueObject>>
      +value: str
    }
    class StudyGroupState {
      <<ValueObject>>
      RECRUITING
      IN_PROGRESS
      ENDED
    }

    StudyGroup "1" *-- "1..*" Member : contains
    StudyGroup --|> StudyGroupId : uses
    StudyGroup --|> StudyGroupState : uses
    Member --|> MemberId : uses
    Member --|> Email : uses
'''


## 핵심 설계 결정
이 도메인 모델은 다음과 같은 DDD의 핵심 원칙과 패턴을 기반으로 설계되었습니다.
### 1. 애그리거트 루트 (Aggregate Root): StudyGroup
- 책임의 경계: StudyGroup은 이 모델의 애그리거트 루트입니다. 멤버 추가/제명, 스터디 시작/종료 등 모든 상태 변경 로직은 StudyGroup을 통해서만 이루어집니다. 이는 애그리거트 내부의 데이터 일관성을 StudyGroup이 스스로 책임지고 강제하도록 합니다.
- 캡슐화: 내부 멤버 목록(_members)은 비공개(private)로 보호됩니다. 외부에서는 오직 복사본(members 속성)만을 읽을 수 있으며, 수정을 위해서는 반드시 add_member와 같은 공식 메서드를 사용해야 합니다. 이는 외부에서 비즈니스 규칙을 우회하여 데이터를 직접 조작하는 것을 방지합니다.
- 팩토리 메서드: 생성자 대신 create라는 정적 팩토리 메서드를 사용합니다. 이를 통해 "스터디를 생성하면, 생성자가 첫 멤버이자 리더가 되며, 초기 상태는 '모집중'이다"와 같은 복잡한 생성 규칙을 캡슐화하고, 객체가 항상 유효한 상태로만 생성됨을 보장합니다.
### 2. 엔티티 (Entity): Member
- 고유 식별성: Member는 StudyGroup 애그리거트 내에서 MemberId라는 고유한 식별자를 가집니다. nickname이나 email이 바뀌더라도, MemberId가 같다면 같은 멤버로 인식됩니다.
- 상태 변경: attendance_count와 같이 시간이 지남에 따라 변할 수 있는 상태를 가지고 있습니다.
### 3. 값 객체 (Value Objects): StudyGroupId, MemberId, Email, StudyGroupState
- 불변성(Immutability): 모든 값 객체는 불변으로 설계되었습니다. 한 번 생성된 값 객체는 그 값을 절대 변경할 수 없습니다. 이는 시스템 전체에서 값을 안전하게 공유하고, 예측 가능성을 높이며, 부작용(side effect)을 방지합니다.
Enum으로 정의된 StudyGroupState는 그 자체로 완벽한 불변성을 가집니다.
StudyGroupId, MemberId, Email 등은 @dataclass(frozen=True)를 사용하여 불변성을 강제합니다.
- 자가 유효성 검사(Self-Validation): Email 값 객체는 생성되는 시점(__post_init__)에 스스로 이메일 형식이 유효한지 검사합니다. 이를 통해 시스템에 유효하지 않은 데이터가 생성되는 것을 원천적으로 차단합니다.
값에 의한 동등성: 내용이 같다면 같은 객체로 취급됩니다. (예: Email("a@a.com") == Email("a@a.com"))

## 구현된 비즈니스 규칙 (Invariants)
StudyGroup 애그리거트는 다음과 같은 비즈니스 규칙(Invariants)을 메서드를 통해 강제합니다. 규칙에 위배될 경우, ValueError 예외를 발생시켜 잘못된 상태 변경을 즉시 중단합니다.
### 멤버 추가 (add_member):
스터디 그룹은 '모집중' 상태일 때만 멤버를 추가할 수 있다.
최대 정원을 초과하여 멤버를 추가할 수 없다.
이미 참여하고 있는 멤버는 다시 추가할 수 없다.
### 스터디 시작 (start_study):
'모집중' 상태의 스터디만 시작할 수 있다.
최소 2명 이상의 멤버가 있어야만 스터디를 시작할 수 있다.
### 멤버 제명 (expel_member):
스터디 그룹의 리더는 스스로를 제명할 수 없다.
### 출석 기록 (record_attendance):
스터디가 '진행중' 상태일 때만 출석을 기록할 수 있다.
import json

import streamlit as st
from openai import OpenAI

# ============================================================
# 1. 기본 설정
# ============================================================
# Streamlit 화면과 OpenAI 모델을 설정한다.

st.title("🕵️ AI Detective")
st.caption("22시 13분의 밀실")


st.info(
    """
📁 사건 파일 #001

사건명: 22시 13분의 밀실

피해자: 한도윤 교수

발생 시간: 오후 10시 13분

발생 장소: 교수의 저택

한도윤 교수는 자신의 서재에서 숨진 채 발견되었습니다.

문은 안에서 잠겨 있었고 외부 침입의 흔적은 발견되지 않았습니다.

현재 용의자는 세 명입니다.

• 집사

• 비서

• 동생

🎯 목표

단서를 수집하고 범인을 찾아내세요.
"""
)


client = OpenAI()
API_MODEL = "gpt-5.4-nano"

# ============================================================
# 2. 사건 데이터
# ============================================================
# 추리 게임에 필요한 장소, 용의자, 단서, 정답 정보를 저장한다.

CASE = {
    "title": "22시 13분의 밀실",
    "culprit": "집사",
    "rooms": {
        "서재": [
            "바닥에 깨진 와인잔이 있다.",
            "벽시계가 22시 13분에 멈춰 있다.",
        ],
        "주방": [
            "싱크대에 젖은 수건이 있다.",
            "쓰레기통에서 찢어진 장갑 조각이 발견된다.",
        ],
        "정원": [
            "창문 아래 진흙 발자국이 있다.",
            "발자국은 집 안쪽을 향하고 있다.",
        ],
    },
    "suspects": {
        "집사": {"statement": "밤 10시부터 계속 주방에 있었습니다."},
        "비서": {"statement": "9시쯤 교수님과 이야기한 뒤 바로 퇴근했습니다."},
        "동생": {"statement": "저녁 내내 정원에서 전화를 하고 있었습니다."},
    },
    "clues": {
        "깨진 와인잔": "잔 표면에서 누군가 급하게 닦은 흔적이 보인다.",
        "멈춘 시계": "시계는 충격으로 인해 22시 13분에 멈춘 것으로 보인다.",
        "젖은 수건": "수건에서 붉은 얼룩이 희미하게 발견된다.",
        "찢어진 장갑": "장갑 크기는 성인 남성용으로 보인다.",
        "진흙 발자국": "발자국은 정원에서 집 안으로 들어온 방향이다.",
    },
}

# ============================================================
# 3. 도구 함수
# ============================================================
# 게임에서 사용할 기능을 정의한다.


def investigate_room(room: str) -> str:
    """특정 장소를 조사한다."""

    if room not in CASE["rooms"]:
        return f"{room}은 조사할 수 없는 장소입니다."

    clues = CASE["rooms"][room]

    return f"{room} 조사 결과: " + " / ".join(clues)


def interrogate_suspect(suspect: str) -> str:
    """용의자를 심문한다."""

    if suspect not in CASE["suspects"]:
        return f"{suspect}이라는 용의자는 없습니다."

    statement = CASE["suspects"][suspect]["statement"]

    return f"{suspect}의 진술: {statement}"


def inspect_clue(clue: str) -> str:
    """발견한 단서를 자세히 조사한다."""

    if clue not in CASE["clues"]:
        return f"{clue}에 대한 상세 정보는 없습니다."

    return f"{clue} 조사 결과: {CASE['clues'][clue]}"


def accuse(suspect: str) -> str:
    """범인을 지목한다."""

    if suspect == CASE["culprit"]:
        return f"정답입니다. 범인은 {suspect}입니다."

    return f"{suspect}은 범인이 아닙니다."


# ============================================================
# 4. Tool Dispatcher
# ============================================================
# 모델이 선택한 도구와 실제 Python 함수를 연결한다.

TOOL_FUNCS = {
    "investigate_room": investigate_room,
    "interrogate_suspect": interrogate_suspect,
    "inspect_clue": inspect_clue,
    "accuse": accuse,
}

# ============================================================
# 5. Tool Schema
# ============================================================
# 모델이 사용할 수 있는 도구와 매개변수를 정의한다.

tools = [
    {
        "type": "function",
        "function": {
            "name": "investigate_room",
            "description": "사건 현장의 장소를 조사하여 단서를 찾는다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "room": {
                        "type": "string",
                        "enum": ["서재", "주방", "정원"],
                        "description": "조사할 장소",
                    }
                },
                "required": ["room"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "interrogate_suspect",
            "description": "용의자를 심문하여 진술을 듣는다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "suspect": {
                        "type": "string",
                        "enum": ["집사", "비서", "동생"],
                        "description": "심문할 용의자",
                    }
                },
                "required": ["suspect"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "inspect_clue",
            "description": "발견한 단서를 자세히 조사한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "clue": {
                        "type": "string",
                        "enum": [
                            "깨진 와인잔",
                            "멈춘 시계",
                            "젖은 수건",
                            "찢어진 장갑",
                            "진흙 발자국",
                        ],
                        "description": "자세히 조사할 단서",
                    }
                },
                "required": ["clue"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "accuse",
            "description": "용의자 중 한 명을 범인으로 지목한다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "suspect": {
                        "type": "string",
                        "enum": ["집사", "비서", "동생"],
                        "description": "범인으로 지목할 용의자",
                    }
                },
                "required": ["suspect"],
            },
        },
    },
]

# ============================================================
# 6. 대화 상태 초기화
# ============================================================
# 이전 대화 내용을 session_state에 저장한다.

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """
너는 추리 게임 '22시 13분의 밀실'의 게임 마스터다.

역할

- 플레이어는 탐정이다.
- 너는 사건 진행을 담당한다.

규칙

1. 장소 조사는 investigate_room 도구를 사용한다.

2. 용의자 심문은 interrogate_suspect 도구를 사용한다.

3. 단서 상세 조사는 inspect_clue 도구를 사용한다.

4. 범인 지목은 accuse 도구를 사용한다.

5. 도구를 사용하지 않고 새로운 단서를 만들어서는 안 된다.

6. 도구 결과에 없는 정보를 추가해서는 안 된다.

7. 단서와 용의자를 임의로 연결해서는 안 된다.

8. 플레이어 대신 행동을 결정해서는 안 된다.

9. 플레이어가 조사하지 않은 정보는 공개해서는 안 된다.

10. 범인을 직접 알려주어서는 안 된다.

11. 답변은 세 문장을 넘지 않는다.

12. 답변 마지막에는 반드시 플레이어가 다음 행동을 선택하도록 유도한다.

예시

잘못된 답변

❌
장갑을 조사해 보겠습니다.

올바른 답변

⭕
다음 행동을 선택하세요.

- 장갑 조사
- 시계 조사
- 정원 조사

잘못된 답변

❌
동생이 범인일 가능성이 높습니다.

올바른 답변

⭕
현재까지 발견된 단서만으로는 판단할 수 없습니다.

반드시 사실만 설명한다.
""",
        }
    ]

# ============================================================
# 7. 기존 대화 출력
# ============================================================
# 저장된 대화 내용을 채팅 화면에 다시 표시한다.

for msg in st.session_state.messages:
    role = msg["role"] if isinstance(msg, dict) else msg.role
    content = msg["content"] if isinstance(msg, dict) else msg.content

    if role in ("user", "assistant") and content:
        st.chat_message(role).write(content)

# ============================================================
# 8. 사용자 입력
# ============================================================
# 사용자의 명령을 입력받는다.

prompt = st.chat_input("예: 서재를 조사해 / 집사를 심문해 / 깨진 와인잔을 조사해")

# ============================================================
# 9. Tool Calling 처리
# ============================================================
# 모델의 응답을 확인하고 필요한 도구를 실행한다.

if prompt:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    st.chat_message("user").write(prompt)

    for _ in range(5):
        response = client.chat.completions.create(
            model=API_MODEL,
            messages=st.session_state.messages,
            tools=tools,
            max_completion_tokens=500,
        )

        msg = response.choices[0].message

        if not msg.tool_calls:
            break

        st.session_state.messages.append(msg)

        for tc in msg.tool_calls:
            args = json.loads(tc.function.arguments)

            result = TOOL_FUNCS[tc.function.name](**args)

            st.caption(f"[도구] {tc.function.name}({args}) → {result}")

            st.session_state.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )

    # ============================================================
    # 10. 최종 응답 출력
    # ============================================================
    # 모델의 응답을 저장하고 화면에 출력한다.

    answer = msg.content or (
        "조사가 너무 복잡해졌습니다. 행동을 하나씩 다시 시도해 주세요."
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    st.chat_message("assistant").write(answer)

import json

import streamlit as st
from openai import OpenAI


# ============================================================
# 1. 기본 설정
# ============================================================
# Streamlit 화면과 OpenAI 모델을 설정한다.

st.title("🕵️ AI Detective")
st.caption("22시 13분의 밀실")

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
            "깨진 와인잔",
            "멈춘 시계",
        ],
        "주방": [
            "젖은 수건",
            "찢어진 장갑",
        ],
        "정원": [
            "진흙 발자국",
        ],
    },

    "room_descriptions": {
        "서재": (
            "서재를 살펴보니 바닥에 깨진 와인잔이 있고, "
            "벽시계는 22시 13분에 멈춰 있다."
        ),
        "주방": (
            "주방의 싱크대에는 젖은 수건이 놓여 있고, "
            "쓰레기통에서는 찢어진 장갑 조각이 발견된다."
        ),
        "정원": (
            "정원의 창문 아래에서 진흙 발자국이 발견된다. "
            "발자국은 집 안쪽을 향하고 있다."
        ),
    },

    "suspects": {
        "집사": {
            "statement": "밤 10시부터 계속 주방에 있었습니다."
        },
        "비서": {
            "statement": "9시쯤 교수님과 이야기한 뒤 바로 퇴근했습니다."
        },
        "동생": {
            "statement": "저녁 내내 정원에서 전화를 하고 있었습니다."
        },
    },

    "clues": {
        "깨진 와인잔":
            "잔 표면에서 누군가 급하게 닦은 흔적이 보인다.",

        "멈춘 시계":
            "시계는 충격으로 인해 22시 13분에 멈춘 것으로 보인다.",

        "젖은 수건":
            "수건에서 붉은 얼룩이 희미하게 발견된다.",

        "찢어진 장갑":
            "장갑 크기는 성인 남성용으로 보인다.",

        "진흙 발자국":
            "발자국은 정원에서 집 안으로 들어온 방향이다.",
    },
}


# ============================================================
# 3. 게임 상태 초기화
# ============================================================
# 이미 조사한 장소, 용의자, 단서를 저장한다.

if "visited_rooms" not in st.session_state:
    st.session_state.visited_rooms = []

if "interrogated_suspects" not in st.session_state:
    st.session_state.interrogated_suspects = []

if "inspected_clues" not in st.session_state:
    st.session_state.inspected_clues = []

if "game_over" not in st.session_state:
    st.session_state.game_over = False


# ============================================================
# 4. 사건 브리핑
# ============================================================

st.info(
    """
📁 사건 파일 #001

**사건명:** 22시 13분의 밀실  
**피해자:** 한도윤 교수  
**발생 시간:** 오후 10시 13분  
**발생 장소:** 교수의 저택  

한도윤 교수는 자신의 서재에서 숨진 채 발견되었습니다.

문은 안에서 잠겨 있었고 외부 침입의 흔적은 발견되지 않았습니다.

현재 용의자는 세 명입니다.

- 집사
- 비서
- 동생

🎯 **목표**

사건 현장을 조사하고 단서를 분석해 범인을 찾아내세요.
"""
)


# ============================================================
# 5. 도구 함수
# ============================================================
# 게임에서 사용할 기능을 정의한다.


def investigate_room(room: str) -> str:
    """특정 장소를 조사한다."""

    if room not in CASE["rooms"]:
        return f"{room}은 조사할 수 없는 장소입니다."

    # 이미 조사한 장소라면 같은 내용을 반복하지 않는다.
    if room in st.session_state.visited_rooms:
        return (
            f"{room}은 이미 조사했습니다. "
            f"새로운 단서는 발견되지 않았습니다."
        )

    st.session_state.visited_rooms.append(room)

    clues = CASE["rooms"][room]
    description = CASE["room_descriptions"][room]

    return (
        f"{description} "
        f"발견한 단서: {', '.join(clues)}"
    )


def interrogate_suspect(suspect: str) -> str:
    """용의자를 심문한다."""

    if suspect not in CASE["suspects"]:
        return f"{suspect}이라는 용의자는 없습니다."

    # 이미 심문한 용의자는 같은 진술을 반복하지 않는다.
    if suspect in st.session_state.interrogated_suspects:
        return (
            f"{suspect}은 이미 심문했습니다. "
            f"추가로 확인된 새로운 진술은 없습니다."
        )

    st.session_state.interrogated_suspects.append(suspect)

    statement = CASE["suspects"][suspect]["statement"]

    return f"{suspect}의 진술: {statement}"


def inspect_clue(clue: str) -> str:
    """발견한 단서를 자세히 조사한다."""

    if clue not in CASE["clues"]:
        return f"{clue}에 대한 상세 정보는 없습니다."

    # 장소 조사 전에 단서를 바로 확인하는 것을 방지한다.
    discovered_clues = []

    for room in st.session_state.visited_rooms:
        discovered_clues.extend(CASE["rooms"][room])

    if clue not in discovered_clues:
        return (
            f"{clue}은 아직 발견하지 않은 단서입니다. "
            f"관련 장소를 먼저 조사해야 합니다."
        )

    # 이미 조사한 단서라면 결과를 반복하지 않는다.
    if clue in st.session_state.inspected_clues:
        return (
            f"{clue}은 이미 자세히 조사했습니다. "
            f"새롭게 확인된 내용은 없습니다."
        )

    st.session_state.inspected_clues.append(clue)

    return f"{clue} 조사 결과: {CASE['clues'][clue]}"


def accuse(suspect: str) -> str:
    """범인을 지목한다."""

    if suspect not in CASE["suspects"]:
        return f"{suspect}이라는 용의자는 없습니다."

    if suspect == CASE["culprit"]:
        st.session_state.game_over = True

        return (
            f"정답입니다. 범인은 {suspect}입니다. "
            f"사건을 해결했습니다."
        )

    return (
        f"{suspect}은 범인이 아닙니다. "
        f"현재까지 확인한 단서를 다시 검토해 보세요."
    )


# ============================================================
# 6. Tool Dispatcher
# ============================================================
# 모델이 선택한 도구와 실제 Python 함수를 연결한다.

TOOL_FUNCS = {
    "investigate_room": investigate_room,
    "interrogate_suspect": interrogate_suspect,
    "inspect_clue": inspect_clue,
    "accuse": accuse,
}


# ============================================================
# 7. Tool Schema
# ============================================================
# 모델이 사용할 수 있는 도구와 매개변수를 정의한다.

tools = [
    {
        "type": "function",
        "function": {
            "name": "investigate_room",
            "description": "사건 현장의 특정 장소를 조사한다.",
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
            "description": "용의자를 심문하여 진술을 확인한다.",
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
            "description": "이미 발견한 단서를 자세히 조사한다.",
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
# 8. 대화 상태 초기화
# ============================================================
# 이전 대화 내용을 session_state에 저장한다.

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": """
너는 추리 게임 '22시 13분의 밀실'의 게임 마스터다.

플레이어는 탐정이며, 너는 사건을 진행하는 역할만 담당한다.

규칙:

1. 장소 조사는 반드시 investigate_room 도구를 사용한다.

2. 용의자 심문은 반드시 interrogate_suspect 도구를 사용한다.

3. 단서 상세 조사는 반드시 inspect_clue 도구를 사용한다.

4. 범인 지목은 반드시 accuse 도구를 사용한다.

5. 도구를 사용하지 않고 새로운 사건 정보나 단서를 만들어내지 않는다.

6. 도구 실행 결과에 없는 사실을 추가하지 않는다.

7. 서로 직접적인 근거가 없는 단서와 용의자를 임의로 연결하지 않는다.

8. 플레이어 대신 다음 행동을 결정하지 않는다.

9. 조사하지 않은 장소나 단서의 내용을 먼저 공개하지 않는다.

10. 범인을 직접 알려주거나 특정 용의자가 범인처럼 보인다고 유도하지 않는다.

11. 이미 조사한 내용은 길게 반복하지 않는다.

12. 매 답변마다 '다음 행동을 선택하세요' 같은 고정 문구를 사용하지 않는다.

13. 사용자가 자유롭게 질문하고 추리할 수 있도록 답변한다.

14. 필요할 때만 짧은 질문으로 대화를 이어간다.

15. 답변은 기본적으로 2~4문장 이내로 작성한다.

16. 게임이 종료되기 전까지는 플레이어의 추론을 대신 결론내리지 않는다.
"""
        }
    ]


# ============================================================
# 9. 기존 대화 출력
# ============================================================
# 저장된 대화 내용을 채팅 화면에 다시 표시한다.

for msg in st.session_state.messages:

    role = msg["role"] if isinstance(msg, dict) else msg.role
    content = msg["content"] if isinstance(msg, dict) else msg.content

    if role in ("user", "assistant") and content:
        st.chat_message(role).write(content)


# ============================================================
# 10. 현재 조사 상태
# ============================================================

with st.sidebar:

    st.subheader("🔎 조사 기록")

    st.write(
        "조사한 장소:",
        ", ".join(st.session_state.visited_rooms)
        if st.session_state.visited_rooms
        else "없음",
    )

    st.write(
        "심문한 용의자:",
        ", ".join(st.session_state.interrogated_suspects)
        if st.session_state.interrogated_suspects
        else "없음",
    )

    st.write(
        "조사한 단서:",
        ", ".join(st.session_state.inspected_clues)
        if st.session_state.inspected_clues
        else "없음",
    )


# ============================================================
# 11. 사용자 입력
# ============================================================

if st.session_state.game_over:

    st.success("🎉 사건을 해결했습니다.")

    prompt = None

else:

    prompt = st.chat_input(
        "사건에 대해 자유롭게 조사하거나 질문해 보세요."
    )


# ============================================================
# 12. Tool Calling 처리
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

            # Tool 호출 과정을 확인하기 위한 실습용 출력
            st.caption(
                f"[도구] {tc.function.name}({args}) → {result}"
            )

            st.session_state.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                }
            )


    # ========================================================
    # 13. 최종 응답 출력
    # ========================================================

    answer = msg.content or (
        "조사가 복잡해졌습니다. 한 가지 행동부터 다시 시도해 주세요."
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
        }
    )

    st.chat_message("assistant").write(answer)
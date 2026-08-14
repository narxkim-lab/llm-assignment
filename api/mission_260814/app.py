import random
import streamlit as st
from openai import OpenAI


# ===================================
# 페이지 설정
# ===================================

st.set_page_config(
    page_title="Detective AI",
    page_icon="🕵️",
    layout="wide"
)


# ===================================
# 스타일
# ===================================

st.markdown(
    """
<style>

/* 전체 화면 폭 */
.block-container {
    max-width: 1200px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

/* 상단 타이틀 */
.detective-header {
    padding: 30px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #111827,
        #1f2937
    );
    text-align: center;
    margin-bottom: 25px;
    border: 1px solid #374151;
}

.detective-header h1 {
    margin: 0;
    font-size: 42px;
    color: #f9fafb;
}

.detective-header p {
    margin-top: 8px;
    margin-bottom: 0;
    color: #d1d5db;
    font-size: 16px;
}

/* 사이드바 버튼 */
div[data-testid="stSidebar"] button {
    border-radius: 10px;
}

/* 채팅창 여백 */
div[data-testid="stChatMessage"] {
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
}

</style>
""",
    unsafe_allow_html=True
)


# ===================================
# OpenAI 설정
# ===================================

client = OpenAI()

API_MODEL = "gpt-5.4-nano"


# ===================================
# 공통 게임 규칙
# ===================================

GAME_RULES = """
너는 추리 게임의 진행자다.

절대로 일반적인 AI 챗봇처럼 행동하지 마라.
현재 진행 중인 사건과 관련된 대화만 진행한다.

반드시 다음 규칙을 지켜라.

1. 사용자는 사건을 조사하는 탐정이다.

2. 너는 사건의 진행자이며
   사건 정보와 진실을 알고 있다.

3. 범인은 사용자가 직접 추리해야 한다.
   사용자가 정답을 제출하기 전에는
   범인의 이름을 절대로 직접 알려 주지 않는다.

4. 사용자가 질문하면
   해당 질문과 관련된 단서를 최대 하나만 공개한다.

5. 한 번에 여러 핵심 단서를 공개하지 않는다.

6. 사용자가 아직 질문하지 않은 핵심 단서를
   임의로 먼저 공개하지 않는다.

7. 사용자가 "단서 정리"라고 입력하면
   지금까지 실제 대화에서 공개한 단서만 정리한다.
   아직 공개하지 않은 단서는 포함하지 않는다.

8. 사용자가 "범인은 ○○다"라고 입력하면
   정답 여부를 판정한다.

9. 사용자가 틀린 범인을 지목했다면
   정답을 알려 주지 않는다.
   "틀렸습니다. 다른 단서를 조사해 보세요."
   정도로만 답한다.

10. 사용자가 맞는 범인을 지목했다면
    반드시 답변에 "정답입니다"라는 표현을 포함한다.

11. 범인을 맞힌 뒤에는
    지금까지의 핵심 단서를 근거로
    왜 그 사람이 범인인지 간단하게 설명한다.

12. 사건과 관련 없는 질문에는 다음과 같이 답한다.

    "현재는 사건 수사 중입니다. 사건과 관련된 질문만 해 주세요."

13. 답변은 최대 3문장으로 작성한다.

14. 존재하지 않는 새로운 인물이나 단서를 임의로 만들지 않는다.
"""


# ===================================
# 사건 목록
# ===================================

CASES = [
    {
        "title": "💎 사라진 다이아몬드",
        "suspects": [
            "집사",
            "요리사",
            "정원사"
        ],
        "description": (
            "저택에서 값비싼 다이아몬드가 사라졌다.\n\n"
            "사건 당시 저택에는 집사, 요리사, 정원사가 있었다.\n\n"
            "세 사람의 진술과 현장의 단서를 조사해 범인을 찾아야 한다."
        ),
        "prompt": """
범인은 정원사다.

사건 정보
- 저택에서 다이아몬드가 사라졌다.

용의자
- 집사
- 요리사
- 정원사

단서
- 집사는 저녁 내내 서재에 있었다.
- 요리사는 주방에서 식사를 준비했다.
- 정원사의 신발에는 젖은 흙이 묻어 있었다.
- 사건 현장의 창문 근처에서 정원 장갑이 발견되었다.
- 다이아몬드는 정원 근처 화분 속에서 발견되었다.
"""
    },

    {
        "title": "🖼️ 박물관 그림 도난 사건",
        "suspects": [
            "경비원",
            "관장",
            "청소부"
        ],
        "description": (
            "폐관 직후 박물관의 대표 작품 한 점이 사라졌다.\n\n"
            "출입 가능성이 있었던 사람은 경비원, 관장, 청소부다.\n\n"
            "각자의 알리바이와 현장 흔적을 조사해야 한다."
        ),
        "prompt": """
범인은 청소부다.

사건 정보
- 박물관에서 유명한 그림이 사라졌다.

용의자
- 경비원
- 관장
- 청소부

단서
- 경비원은 사건 당시 다른 전시실을 순찰하고 있었다.
- 관장은 직원 회의에 참석하고 있었다.
- 청소부는 사건 직전 해당 전시실을 청소했다.
- 청소부의 카트에서 그림 액자의 작은 조각이 발견되었다.
- CCTV에는 커다란 천으로 무언가를 가린 카트가 이동하는 장면이 찍혔다.
"""
    },

    {
        "title": "📝 시험지 유출 사건",
        "suspects": [
            "교사",
            "학생",
            "행정 직원"
        ],
        "description": (
            "중요한 시험을 하루 앞두고 시험 문제가 외부로 유출됐다.\n\n"
            "시험 파일에 접근할 수 있었던 세 사람이 용의선상에 올랐다.\n\n"
            "파일 기록과 진술을 비교해 범인을 찾아야 한다."
        ),
        "prompt": """
범인은 행정 직원이다.

사건 정보
- 시험 문제가 외부로 유출되었다.

용의자
- 교사
- 학생
- 행정 직원

단서
- 교사는 사건 당시 수업 중이었다.
- 학생은 도서관 출입 기록이 확인되었다.
- 행정 직원은 시험 파일이 저장된 컴퓨터에 접근 권한이 있었다.
- 행정 직원의 계정으로 심야 시간에 파일이 열렸다.
- 외부 저장장치 연결 기록도 같은 시간에 남아 있었다.
"""
    },

    {
        "title": "💍 호텔 보석 절도 사건",
        "suspects": [
            "투숙객",
            "직원",
            "매니저"
        ],
        "description": (
            "호텔 객실에서 고가의 보석이 사라졌다.\n\n"
            "사건 시간에 해당 층을 오갈 수 있었던 사람은 세 명이다.\n\n"
            "객실 출입 기록과 CCTV를 조사해야 한다."
        ),
        "prompt": """
범인은 투숙객이다.

사건 정보
- 호텔 객실에서 보석이 사라졌다.

용의자
- 투숙객
- 직원
- 매니저

단서
- 직원은 사건 당시 로비 업무 중이었다.
- 매니저는 보안실에서 CCTV를 확인하고 있었다.
- 같은 층의 투숙객 한 명이 사건 직전 복도에 있었다.
- 해당 투숙객의 가방에서 빈 보석 상자가 발견되었다.
- 객실 출입 시간과 투숙객의 이동 시간이 일치했다.
"""
    }
]


# ===================================
# 사건 프롬프트 생성
# ===================================

def build_system_prompt(case):

    return (
        GAME_RULES
        + "\n\n"
        + case["prompt"]
    )


# ===================================
# 사건 / 메시지 초기화
# ===================================

if "case_index" not in st.session_state:

    st.session_state.case_index = random.randrange(
        len(CASES)
    )


if "messages" not in st.session_state:

    current_case = CASES[
        st.session_state.case_index
    ]

    st.session_state.messages = [
        {
            "role": "system",
            "content": build_system_prompt(
                current_case
            )
        }
    ]


current_case = CASES[
    st.session_state.case_index
]


# ===================================
# 상단 헤더
# ===================================

st.markdown(
    """
<div class="detective-header">
    <h1>🕵️ DETECTIVE AI</h1>
    <p>The Mystery Case Files</p>
</div>
""",
    unsafe_allow_html=True
)


# ===================================
# 사이드바
# ===================================

with st.sidebar:

    st.markdown(
        "## 🗂️ CASE FILE"
    )

    st.markdown(
        f"### {current_case['title']}"
    )

    st.markdown(
        "**현재 용의자**"
    )

    for suspect in current_case["suspects"]:

        st.write(
            f"👤 {suspect}"
        )

    st.divider()

    st.markdown(
        """
### 🎯 임무

질문과 단서를 통해  
**진짜 범인을 찾아내세요.**
"""
    )

    st.divider()

    st.markdown(
        """
### 📜 게임 규칙

- 질문을 통해 정보를 수집합니다.
- AI는 단서를 하나씩 공개합니다.
- `단서 정리`로 공개된 정보를 정리할 수 있습니다.
- 범인을 찾았다면 `범인은 ○○다`라고 입력하세요.
"""
    )

    st.divider()

    if st.button(
        "🔄 새로운 사건 시작",
        use_container_width=True
    ):

        # 현재 사건을 제외한 사건 목록
        available_indexes = [
            index
            for index in range(
                len(CASES)
            )
            if index
            != st.session_state.case_index
        ]

        # 새로운 사건 선택
        st.session_state.case_index = (
            random.choice(
                available_indexes
            )
        )

        new_case = CASES[
            st.session_state.case_index
        ]

        # 대화 기록도 새로운 사건으로 초기화
        st.session_state.messages = [
            {
                "role": "system",
                "content": build_system_prompt(
                    new_case
                )
            }
        ]

        st.rerun()


# ===================================
# 사건 브리핑
# ===================================

with st.container(
    border=True
):

    st.markdown(
        "### 📜 사건 브리핑"
    )

    st.markdown(
        f"## {current_case['title']}"
    )

    st.write(
        current_case["description"]
    )


# ===================================
# 용의자 카드
# ===================================

st.markdown(
    "### 👥 주요 용의자"
)

col1, col2, col3 = st.columns(
    3
)

suspect_columns = [
    col1,
    col2,
    col3
]


for index, (
    column,
    suspect
) in enumerate(
    zip(
        suspect_columns,
        current_case["suspects"]
    ),
    start=1
):

    with column:

        with st.container(
            border=True
        ):

            st.caption(
                f"SUSPECT {index:02d}"
            )

            st.markdown(
                f"### 👤 {suspect}"
            )

            st.caption(
                "조사 필요"
            )


# ===================================
# 처음 접속했을 때 안내
# ===================================

if len(
    st.session_state.messages
) == 1:

    with st.container(
        border=True
    ):

        st.markdown(
            "### 🔍 수사를 시작하세요"
        )

        st.write(
            """
용의자의 알리바이, 사건 현장,
발견된 물건 등에 대해 질문할 수 있습니다.

충분한 단서를 확보했다면
**"범인은 ○○다"**라고 추리해 보세요.
"""
        )

        st.markdown(
            "**💡 질문 예시**"
        )

        st.markdown(
            """
- 첫 번째 용의자는 사건 당시 어디에 있었어?
- 사건 현장에서 발견된 물건이 있어?
- 세 번째 용의자에 대한 단서를 알려 줘.
- 단서 정리.
"""
        )


st.divider()


# ===================================
# 수사 기록
# ===================================

st.markdown(
    "### 🔎 수사 기록"
)


# 이전 대화 출력
for msg in (
    st.session_state.messages
):

    if msg["role"] == "system":
        continue

    if msg["role"] == "user":

        with st.chat_message(
            "user",
            avatar="🕵️"
        ):

            st.write(
                msg["content"]
            )

    elif (
        msg["role"]
        == "assistant"
    ):

        with st.chat_message(
            "assistant",
            avatar="📁"
        ):

            st.write(
                msg["content"]
            )


# ===================================
# 사용자 입력
# ===================================

prompt = st.chat_input(
    "🔍 사건에 대해 질문하거나 범인을 추리하세요..."
)


if prompt:

    # -----------------------------------
    # 사용자 메시지 저장
    # -----------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # -----------------------------------
    # 사용자 메시지 화면 출력
    # -----------------------------------

    with st.chat_message(
        "user",
        avatar="🕵️"
    ):

        st.write(
            prompt
        )


    # ===================================
    # OpenAI API 호출
    # ===================================

    with st.spinner(
        "사건 기록을 조사하는 중... 🔍"
    ):

        response = (
            client.chat.completions.create(
                model=API_MODEL,
                messages=(
                    st.session_state.messages
                ),
                max_completion_tokens=400
            )
        )


    answer = (
        response
        .choices[0]
        .message
        .content
    )


    # ===================================
    # AI 응답 출력
    # ===================================

    with st.chat_message(
        "assistant",
        avatar="📁"
    ):

        st.write(
            answer
        )


    # ===================================
    # AI 응답 저장
    # ===================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    # ===================================
    # 정답 연출
    # ===================================

    if (
        "정답입니다" in answer
        or "사건을 해결" in answer
    ):

        st.success(
            "🏆 사건 해결! 범인을 정확하게 찾아냈습니다."
        )

        st.balloons()
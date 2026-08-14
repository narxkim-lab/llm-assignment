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

    /* 사건 브리핑 */
    .case-card {
        padding: 22px;
        border-radius: 16px;
        border: 1px solid #4b5563;
        margin-bottom: 18px;
        background-color: rgba(31, 41, 55, 0.18);
    }

    .case-title {
        font-size: 25px;
        font-weight: 700;
        margin-bottom: 10px;
    }

    .case-description {
        opacity: 0.85;
        line-height: 1.7;
    }

    /* 작은 안내 카드 */
    .guide-card {
        padding: 16px;
        border-radius: 12px;
        border-left: 4px solid #f59e0b;
        background-color: rgba(245, 158, 11, 0.08);
        margin-bottom: 18px;
    }

    /* 사이드바 버튼 */
    div[data-testid="stSidebar"] button {
        border-radius: 10px;
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
# 사건 목록
# ===================================

CASES = [
    {
        "title": "💎 사라진 다이아몬드",
        "suspects": ["집사", "요리사", "정원사"],
        "description": """
        저택에서 값비싼 다이아몬드가 사라졌다.
        사건 당시 저택에는 집사, 요리사, 정원사가 있었다.
        세 사람의 진술과 현장의 단서를 조사해 범인을 찾아야 한다.
        """,
        "prompt": """
너는 추리 게임 진행자다.

게임 규칙
- 범인을 직접 알려 주지 않는다.
- 사용자가 질문하면 관련된 단서를 하나씩 제공한다.
- 한 번에 지나치게 많은 단서를 공개하지 않는다.
- 아직 공개하지 않은 핵심 단서를 먼저 말하지 않는다.
- 사용자가 '단서 정리'를 요청하면 지금까지 대화에서 공개된 단서만 정리한다.
- 사용자가 '범인은 ○○다'라고 입력하면 정답 여부를 판정한다.
- 틀렸다면 정답을 알려 주지 않고 다시 추리할 기회를 준다.
- 답변은 최대 3문장으로 작성한다.

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
        "suspects": ["경비원", "관장", "청소부"],
        "description": """
        폐관 직후 박물관의 대표 작품 한 점이 사라졌다.
        출입 가능성이 있었던 사람은 경비원, 관장, 청소부다.
        각자의 알리바이와 현장 흔적을 조사해야 한다.
        """,
        "prompt": """
너는 추리 게임 진행자다.

게임 규칙
- 범인을 직접 알려 주지 않는다.
- 사용자가 질문하면 관련된 단서를 하나씩 제공한다.
- 한 번에 지나치게 많은 단서를 공개하지 않는다.
- 아직 공개하지 않은 핵심 단서를 먼저 말하지 않는다.
- 사용자가 '단서 정리'를 요청하면 지금까지 대화에서 공개된 단서만 정리한다.
- 사용자가 '범인은 ○○다'라고 입력하면 정답 여부를 판정한다.
- 틀렸다면 정답을 알려 주지 않고 다시 추리할 기회를 준다.
- 답변은 최대 3문장으로 작성한다.

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
        "suspects": ["교사", "학생", "행정 직원"],
        "description": """
        중요한 시험을 하루 앞두고 시험 문제가 외부로 유출됐다.
        시험 파일에 접근할 수 있었던 세 사람이 용의선상에 올랐다.
        파일 기록과 진술을 비교해 범인을 찾아야 한다.
        """,
        "prompt": """
너는 추리 게임 진행자다.

게임 규칙
- 범인을 직접 알려 주지 않는다.
- 사용자가 질문하면 관련된 단서를 하나씩 제공한다.
- 한 번에 지나치게 많은 단서를 공개하지 않는다.
- 아직 공개하지 않은 핵심 단서를 먼저 말하지 않는다.
- 사용자가 '단서 정리'를 요청하면 지금까지 대화에서 공개된 단서만 정리한다.
- 사용자가 '범인은 ○○다'라고 입력하면 정답 여부를 판정한다.
- 틀렸다면 정답을 알려 주지 않고 다시 추리할 기회를 준다.
- 답변은 최대 3문장으로 작성한다.

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
        "suspects": ["투숙객", "직원", "매니저"],
        "description": """
        호텔 객실에서 고가의 보석이 사라졌다.
        사건 시간에 해당 층을 오갈 수 있었던 사람은 세 명이다.
        객실 출입 기록과 CCTV를 조사해야 한다.
        """,
        "prompt": """
너는 추리 게임 진행자다.

게임 규칙
- 범인을 직접 알려 주지 않는다.
- 사용자가 질문하면 관련된 단서를 하나씩 제공한다.
- 한 번에 지나치게 많은 단서를 공개하지 않는다.
- 아직 공개하지 않은 핵심 단서를 먼저 말하지 않는다.
- 사용자가 '단서 정리'를 요청하면 지금까지 대화에서 공개된 단서만 정리한다.
- 사용자가 '범인은 ○○다'라고 입력하면 정답 여부를 판정한다.
- 틀렸다면 정답을 알려 주지 않고 다시 추리할 기회를 준다.
- 답변은 최대 3문장으로 작성한다.

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
# 사건 / 메시지 초기화
# ===================================

if "case_index" not in st.session_state:
    st.session_state.case_index = random.randrange(len(CASES))

if "messages" not in st.session_state:
    current_case = CASES[st.session_state.case_index]

    st.session_state.messages = [
        {
            "role": "system",
            "content": current_case["prompt"]
        }
    ]


current_case = CASES[st.session_state.case_index]


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

    st.markdown("## 🗂️ CASE FILE")

    st.markdown(
        f"""
### {current_case["title"]}

**현재 용의자**

👤 {current_case["suspects"][0]}

👤 {current_case["suspects"][1]}

👤 {current_case["suspects"][2]}
"""
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
- AI는 단서를 조금씩 공개합니다.
- `단서 정리`로 정보를 정리할 수 있습니다.
- 범인을 찾았다면  
  `범인은 ○○다`라고 입력하세요.
"""
    )

    st.divider()

    if st.button(
        "🔄 새로운 사건 시작",
        use_container_width=True
    ):

        # 현재 사건과 다른 사건 선택
        available_indexes = [
            index
            for index in range(len(CASES))
            if index != st.session_state.case_index
        ]

        st.session_state.case_index = random.choice(
            available_indexes
        )

        new_case = CASES[
            st.session_state.case_index
        ]

        # 새로운 사건으로 대화 초기화
        st.session_state.messages = [
            {
                "role": "system",
                "content": new_case["prompt"]
            }
        ]

        st.rerun()


# ===================================
# 메인 화면 - 사건 브리핑
# ===================================

st.markdown(
    f"""
    <div class="case-card">

        <div class="case-title">
            📜 사건 브리핑
        </div>

        <h3>{current_case["title"]}</h3>

        <div class="case-description">
            {current_case["description"]}
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ===================================
# 용의자 카드
# ===================================

st.subheader("👥 주요 용의자")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="용의자 01",
        value=f"👤 {current_case['suspects'][0]}"
    )

with col2:
    st.metric(
        label="용의자 02",
        value=f"👤 {current_case['suspects'][1]}"
    )

with col3:
    st.metric(
        label="용의자 03",
        value=f"👤 {current_case['suspects'][2]}"
    )


# ===================================
# 처음 접속했을 때 안내
# ===================================

if len(st.session_state.messages) == 1:

    st.markdown(
        """
        <div class="guide-card">

        <b>🔍 수사를 시작하세요.</b><br><br>

        용의자의 알리바이, 사건 현장,
        발견된 물건 등에 대해 질문할 수 있습니다.<br>

        충분한 단서를 확보했다면
        <b>"범인은 ○○다"</b>라고 추리해 보세요.

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
**💡 질문 예시**

- 집사는 사건 당시 어디에 있었어?
- 사건 현장에서 발견된 물건이 있어?
- 정원사에 대한 단서를 알려 줘.
- 단서 정리.
"""
    )


st.divider()


# ===================================
# 수사 기록
# ===================================

st.subheader("🔎 수사 기록")


# 이전 대화 출력
for msg in st.session_state.messages:

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

    elif msg["role"] == "assistant":

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

    # 사용자 메시지 저장
    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # 사용자 메시지 표시
    with st.chat_message(
        "user",
        avatar="🕵️"
    ):
        st.write(prompt)

    # ===================================
    # OpenAI API 호출
    # ===================================

    with st.spinner(
        "사건 기록을 조사하는 중... 🔍"
    ):

        response = client.chat.completions.create(
            model=API_MODEL,
            messages=st.session_state.messages,
            max_completion_tokens=400
        )

    answer = response.choices[0].message.content

    # ===================================
    # AI 응답 출력
    # ===================================

    with st.chat_message(
        "assistant",
        avatar="📁"
    ):
        st.write(answer)

    # AI 응답 저장
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    # ===================================
    # 정답 연출
    # ===================================

    # AI가 정답이라고 판정한 경우
    if (
        "정답입니다" in answer
        or "사건을 해결" in answer
    ):

        st.success(
            "🏆 사건 해결! 범인을 정확하게 찾아냈습니다."
        )

        st.balloons()
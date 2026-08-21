"""RAG 추리 사건 파일 — Streamlit 게임."""

from __future__ import annotations

import os

import streamlit as st

from rag import CHROMA_DIR, ask_investigator, get_store, load_cases, store_count

st.set_page_config(page_title="RAG 추리 사건 파일", page_icon="🕵️", layout="wide")
st.markdown(
    """
    <style>
      .stApp {background: linear-gradient(135deg, #111827 0%, #1f2937 55%, #312e2a 100%);}
      [data-testid="stHeader"] {background: transparent;}
      .case-file {border: 1px solid #8b7355; border-radius: 12px; padding: 1.2rem;
                  background: rgba(247, 239, 218, .08); margin-bottom: 1rem;}
      .stamp {display:inline-block; border:2px solid #ef4444; color:#f87171; padding:.2rem .6rem;
              transform:rotate(-3deg); font-weight:700; letter-spacing:.12rem;}
      .clue {border-left: 4px solid #d4a853; padding-left: .8rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

cases = load_cases()
case_by_id = {case["id"]: case for case in cases}

defaults = {"score": 0, "solved": set(), "attempts": {}, "last_case": None}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

with st.sidebar:
    st.markdown("### 🗃️ 사건 보관소")
    selected_id = st.selectbox(
        "수사할 사건",
        options=list(case_by_id),
        format_func=lambda value: case_by_id[value]["title"],
    )
    case = case_by_id[selected_id]
    st.caption(f"난이도 · {case['difficulty']}")
    st.metric("해결한 사건", f"{len(st.session_state.solved)} / {len(cases)}")
    st.metric("탐정 점수", f"{st.session_state.score}점")
    evidence_k = st.slider("검색할 기록 수", 2, 5, 3)
    if st.button("게임 기록 초기화", use_container_width=True):
        st.session_state.score = 0
        st.session_state.solved = set()
        st.session_state.attempts = {}
        st.rerun()

st.title("🕵️ RAG 추리 사건 파일")
st.caption("사건 기록을 검색하고, 진술의 모순을 찾아 범인을 지목하세요.")

left, right = st.columns([3, 1])
with left:
    st.markdown(f"## {case['title']}")
    st.markdown(f"*{case['subtitle']}*")
with right:
    status = "해결 완료" if selected_id in st.session_state.solved else "수사 중"
    st.markdown(f'<span class="stamp">{status}</span>', unsafe_allow_html=True)

st.markdown(f'<div class="case-file">{case["briefing"]}</div>', unsafe_allow_html=True)

suspect_columns = st.columns(len(case["suspects"]))
for column, suspect in zip(suspect_columns, case["suspects"]):
    with column:
        st.markdown(f"### {suspect['emoji']} {suspect['name']}")
        st.caption(suspect["role"])

brief_tab, search_tab, accuse_tab = st.tabs(["📋 수사 안내", "🔎 기록 검색", "⚖️ 범인 지목"])

with brief_tab:
    st.markdown(
        """
        1. **기록 검색**에서 시간, 장소, 장비 또는 용의자에 관해 질문합니다.
        2. 검색된 원문 근거와 진술을 비교해 모순을 찾습니다.
        3. 확신이 들면 **범인 지목**에서 한 명을 선택합니다.
        """
    )
    st.info("예시 질문: ‘정전 기록은 어떻게 돼?’, ‘유나의 진술과 오븐 기록을 비교해줘.’")

index_ready = CHROMA_DIR.exists() and any(CHROMA_DIR.iterdir())

with search_tab:
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("OPENAI_API_KEY가 없어 RAG 질문 기능을 사용할 수 없습니다.")
    elif not index_ready:
        st.warning("먼저 터미널에서 `python build_index.py`를 실행해 사건 기록을 인덱싱하세요.")
    else:
        @st.cache_resource
        def cached_store():
            return get_store()

        store = cached_store()
        st.caption(f"현재 사건 기록 전체 {store_count(store)}개 조각")
        with st.form("question_form"):
            question = st.text_input("기록 담당 수사관에게 질문", placeholder="누구의 진술이 기계 기록과 다르지?")
            ask = st.form_submit_button("기록 검색", type="primary")

        if ask and question.strip():
            with st.spinner("관련 사건 기록을 찾는 중..."):
                try:
                    answer, documents = ask_investigator(store, selected_id, question, k=evidence_k)
                except Exception as exc:
                    st.error(f"API 요청에 실패했습니다: {exc}")
                else:
                    st.markdown("#### 수사관 답변")
                    st.write(answer)
                    st.markdown("#### 검색된 원문 기록")
                    for number, document in enumerate(documents, 1):
                        label = document.metadata.get("detail") or document.metadata.get("record") or "사건 기록"
                        with st.expander(f"[{number}] {label}"):
                            st.caption(f"{document.metadata['source']} · {document.metadata['chunk_id']}")
                            st.markdown(document.page_content)

with accuse_tab:
    if selected_id in st.session_state.solved:
        st.success(f"정답은 **{case['culprit']}**입니다. 사건을 해결했습니다!")
        st.markdown(f'<div class="clue">{case["solution"]}</div>', unsafe_allow_html=True)
        st.markdown("**결정적 근거:** " + " · ".join(case["key_evidence"]))
    else:
        with st.form("accusation_form"):
            accused = st.radio(
                "누가 범인이라고 생각하나요?",
                [suspect["name"] for suspect in case["suspects"]],
                index=None,
            )
            reason = st.text_area("추리 근거 (선택)", placeholder="진술과 기록의 모순을 적어보세요.")
            submit = st.form_submit_button("최종 지목", type="primary")

        if submit:
            if accused is None:
                st.warning("용의자를 한 명 선택하세요.")
            elif accused == case["culprit"]:
                st.session_state.solved.add(selected_id)
                st.session_state.score += max(30 - st.session_state.attempts.get(selected_id, 0) * 10, 10)
                st.success(f"정답입니다! 범인은 **{accused}**입니다.")
                st.markdown(f'<div class="clue">{case["solution"]}</div>', unsafe_allow_html=True)
                st.balloons()
            else:
                attempts = st.session_state.attempts.get(selected_id, 0) + 1
                st.session_state.attempts[selected_id] = attempts
                hint = case["hints"][min(attempts - 1, len(case["hints"]) - 1)]
                st.error(f"{accused}은(는) 결정적 기록과 맞지 않습니다. 다시 조사해 보세요.")
                st.info(f"💡 힌트: {hint}")


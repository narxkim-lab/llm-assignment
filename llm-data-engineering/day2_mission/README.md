# 🕵️ RAG 추리 사건 파일

사건 기록을 벡터 검색하고 진술의 모순을 찾아 범인을 맞히는 작은 Streamlit 게임입니다. 수업에서 다룬 **Markdown 청킹 → OpenAI 임베딩 → Chroma 검색 → Responses API 답변** 흐름을 하나의 앱으로 묶었습니다.

## 주요 기능

- 난이도가 다른 추리 사건 3개
- 선택한 사건 내부로 제한한 메타데이터 검색
- 검색 근거 번호가 붙는 수사관 답변
- 원문 기록과 출처 확인
- 오답 힌트, 사건별 점수와 해결 기록
- 정답을 검색 말뭉치와 분리해 직접 노출 방지

## 실행 방법

프로젝트에 이미 설치된 가상환경을 사용할 경우:

```bash
cd day2_mission
export OPENAI_API_KEY="발급받은_API_키"
../.venv/bin/python build_index.py
../.venv/bin/streamlit run app.py
```

새 환경에서는 먼저 의존성을 설치합니다.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python build_index.py
streamlit run app.py
```

브라우저에서 표시된 로컬 주소(기본값 `http://localhost:8501`)를 엽니다.

## 프로젝트 구조

```text
day2_mission/
├── corpus/raw/          # 검색 가능한 사건 원문
├── data/cases.json      # 게임 정보와 정답(벡터 DB에는 저장하지 않음)
├── rag.py               # 청킹·검색·Responses API 호출
├── build_index.py       # Chroma 인덱스 생성
├── app.py               # Streamlit 게임 화면
└── tests/test_rag.py    # API 호출 없는 데이터 테스트
```

## 테스트

```bash
cd day2_mission
../.venv/bin/python -m unittest discover -s tests -v
```

`CHAT_MODEL`과 `EMBED_MODEL` 환경 변수로 모델을 변경할 수 있습니다. 기본값은 수업 예제와 동일한 `gpt-5.6-luna`, `text-embedding-3-small`입니다.

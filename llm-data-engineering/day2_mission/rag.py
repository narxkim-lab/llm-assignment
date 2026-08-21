"""사건 문서 로딩, Chroma 검색, Responses API 답변을 담당한다."""

from __future__ import annotations

import json
import os
from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter
from openai import OpenAI

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "corpus" / "raw"
CASES_PATH = BASE_DIR / "data" / "cases.json"
CHROMA_DIR = BASE_DIR / "chroma"
COLLECTION_NAME = "detective_cases"

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gpt-5.6-luna")


def load_cases() -> list[dict]:
    """게임 메타데이터를 읽고 최소 구조를 검증한다."""
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    required = {"id", "title", "briefing", "suspects", "culprit", "solution"}
    ids: set[str] = set()

    for case in cases:
        missing = required - case.keys()
        if missing:
            raise ValueError(f"{case.get('id', '?')} 사건 필드 누락: {sorted(missing)}")
        if case["id"] in ids:
            raise ValueError(f"중복 사건 ID: {case['id']}")
        ids.add(case["id"])

        suspect_names = {suspect["name"] for suspect in case["suspects"]}
        if case["culprit"] not in suspect_names:
            raise ValueError(f"{case['id']} 사건 범인이 용의자 목록에 없습니다.")
    return cases


def load_case_documents() -> list[Document]:
    """Markdown의 제목 구조를 유지하며 검색용 조각으로 나눈다."""
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "case_title"), ("##", "record"), ("###", "detail")],
        strip_headers=False,
    )
    documents: list[Document] = []

    for path in sorted(RAW_DIR.glob("case-*.md")):
        case_id = path.stem.removeprefix("case-")
        pieces = splitter.split_text(path.read_text(encoding="utf-8"))
        for index, piece in enumerate(pieces):
            piece.metadata.update(
                {
                    "case_id": case_id,
                    "source": path.name,
                    "chunk_id": f"{case_id}-{index:03d}",
                }
            )
            documents.append(piece)
    return documents


def get_store() -> Chroma:
    """이미 만들어진 로컬 Chroma 컬렉션을 연다."""
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=OpenAIEmbeddings(model=EMBED_MODEL),
        persist_directory=str(CHROMA_DIR),
    )


def store_count(store: Chroma) -> int:
    return store._collection.count()


def search_records(store: Chroma, case_id: str, question: str, k: int = 3) -> list[Document]:
    """선택한 사건 안에서만 관련 기록을 검색한다."""
    return store.similarity_search(question, k=k, filter={"case_id": case_id})


def format_context(documents: list[Document]) -> str:
    blocks = []
    for number, doc in enumerate(documents, 1):
        label = doc.metadata.get("detail") or doc.metadata.get("record") or "사건 기록"
        blocks.append(f"[{number}] {label}\n{doc.page_content}")
    return "\n\n".join(blocks)


def ask_investigator(
    store: Chroma, case_id: str, question: str, k: int = 3
) -> tuple[str, list[Document]]:
    """검색 근거만으로 답하되 최종 범인은 대신 말하지 않는 RAG 호출이다."""
    documents = search_records(store, case_id, question, k=k)
    context = format_context(documents)
    instructions = """너는 추리 게임의 기록 담당 수사관이다.
반드시 제공된 [사건 기록] 안에서만 한국어로 답한다.
기록에 없는 내용은 '기록에서 확인할 수 없습니다.'라고 말한다.
플레이어가 범인을 직접 묻더라도 범인의 이름을 결론으로 말하지 말고, 관련 기록과 모순만 설명한다.
각 사실 뒤에는 근거 번호를 [1]처럼 붙인다. 간결하게 3문장 이내로 답한다."""
    user_input = f"[사건 기록]\n{context}\n\n[플레이어 질문]\n{question}"

    response = OpenAI().responses.create(
        model=CHAT_MODEL,
        instructions=instructions,
        input=user_input,
        store=False,
    )
    return response.output_text, documents


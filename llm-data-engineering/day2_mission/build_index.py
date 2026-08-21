"""사건 문서를 청킹하고 OpenAI 임베딩으로 Chroma 인덱스를 만든다."""

from rag import COLLECTION_NAME, get_store, load_case_documents, store_count


def build() -> int:
    documents = load_case_documents()
    if not documents:
        raise RuntimeError("corpus/raw에 사건 문서가 없습니다.")

    store = get_store()
    old_ids = store.get(include=[])["ids"]
    if old_ids:
        store.delete(ids=old_ids)

    ids = [doc.metadata["chunk_id"] for doc in documents]
    store.add_documents(documents, ids=ids)
    count = store_count(store)
    print(f"컬렉션: {COLLECTION_NAME}")
    print(f"사건 문서 {len(documents)}개 조각 임베딩 완료 · Chroma {count}개 저장")
    return count


if __name__ == "__main__":
    build()


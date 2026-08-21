import unittest

from rag import format_context, load_case_documents, load_cases


class CorpusTest(unittest.TestCase):
    def test_cases_have_valid_culprits(self):
        cases = load_cases()
        self.assertEqual(len(cases), 3)
        for case in cases:
            names = {suspect["name"] for suspect in case["suspects"]}
            self.assertIn(case["culprit"], names)
            self.assertGreaterEqual(len(case["key_evidence"]), 3)

    def test_documents_are_chunked_and_tagged(self):
        documents = load_case_documents()
        self.assertGreaterEqual(len(documents), 12)
        self.assertEqual({doc.metadata["case_id"] for doc in documents}, {"meteorite", "bakery", "mask"})
        self.assertEqual(len({doc.metadata["chunk_id"] for doc in documents}), len(documents))

    def test_context_has_numbered_citations(self):
        context = format_context(load_case_documents()[:2])
        self.assertIn("[1]", context)
        self.assertIn("[2]", context)


if __name__ == "__main__":
    unittest.main()


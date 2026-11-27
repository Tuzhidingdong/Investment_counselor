import unittest
from pathlib import Path

from scripts.flex_parser import normalize_flex_xml


class FlexParserTests(unittest.TestCase):
    def setUp(self):
        self.xml = (Path(__file__).parent / "fixtures" / "sample_flex.xml").read_text(encoding="utf-8")

    def test_normalizes_sections_and_masks_account_id(self):
        result = normalize_flex_xml(self.xml)
        self.assertEqual(result["query_name"], "Counselor Test")
        self.assertTrue(result["coverage"]["open_positions"])
        self.assertTrue(result["coverage"]["trades"])
        statement = result["statements"][0]
        self.assertEqual(statement["account_id_masked"], "***4567")
        self.assertEqual(statement["account_information"][0]["account_id_masked"], "***4567")
        self.assertEqual(statement["open_positions"][0]["currency"], "USD")
        self.assertNotIn("U1234567", str(result))

    def test_rejects_error_or_non_statement_xml(self):
        with self.assertRaises(ValueError):
            normalize_flex_xml("<FlexStatementResponse><Status>Fail</Status></FlexStatementResponse>")
        with self.assertRaises(ValueError):
            normalize_flex_xml("<FlexQueryResponse><FlexStatements count='0'/></FlexQueryResponse>")


if __name__ == "__main__":
    unittest.main()

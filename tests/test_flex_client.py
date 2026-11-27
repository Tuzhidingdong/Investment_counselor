import unittest
from scripts.flex_sync import _parse_service_error


class FlexClientTests(unittest.TestCase):
    def test_detects_ibkr_error_xml(self):
        data = b'<FlexStatementResponse><Status>Fail</Status><ErrorCode>1012</ErrorCode><ErrorMessage>Token has expired.</ErrorMessage></FlexStatementResponse>'
        self.assertEqual(_parse_service_error(data), ("1012", "Token has expired.", "Fail"))

    def test_success_is_not_an_error(self):
        data = b'<FlexStatementResponse><Status>Success</Status><ReferenceCode>123456</ReferenceCode></FlexStatementResponse>'
        self.assertIsNone(_parse_service_error(data))

    def test_transient_codes_cover_generation_and_pacing_errors(self):
        from scripts.flex_sync import TRANSIENT_ERROR_CODES
        self.assertTrue({"1003", "1004", "1005", "1006", "1007", "1008", "1009", "1018", "1019", "1021"}.issubset(TRANSIENT_ERROR_CODES))
        self.assertNotIn("1012", TRANSIENT_ERROR_CODES)  # Expired token is not retryable.


if __name__ == "__main__":
    unittest.main()

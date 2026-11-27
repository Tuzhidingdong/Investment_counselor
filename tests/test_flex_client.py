import unittest
from scripts.flex_sync import _parse_service_error


class FlexClientTests(unittest.TestCase):
    def test_detects_ibkr_error_xml(self):
        data = b'<FlexStatementResponse><Status>Fail</Status><ErrorCode>1012</ErrorCode><ErrorMessage>Token has expired.</ErrorMessage></FlexStatementResponse>'
        self.assertEqual(_parse_service_error(data), ("1012", "Token has expired.", "Fail"))

    def test_success_is_not_an_error(self):
        data = b'<FlexStatementResponse><Status>Success</Status><ReferenceCode>123456</ReferenceCode></FlexStatementResponse>'
        self.assertIsNone(_parse_service_error(data))


if __name__ == "__main__":
    unittest.main()

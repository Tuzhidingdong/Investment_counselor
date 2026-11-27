import unittest
from scripts.portfolio_snapshot import summarize


class PortfolioSummaryTests(unittest.TestCase):
    def test_currency_totals_are_not_blended(self):
        snapshot = {
            "source": "test",
            "coverage": {"open_positions": True},
            "statements": [{
                "account_id_masked": "***4567",
                "open_positions": [
                    {"symbol": "A", "positionValue": "100.50", "currency": "USD"},
                    {"symbol": "B", "positionValue": "50", "currency": "SGD"},
                    {"symbol": "C", "positionValue": "n/a", "currency": "USD"},
                ],
                "equity_summaries": [{"currency": "USD", "total": "1000"}],
                "cash_reports": [{"currency": "SGD", "endingCash": "200"}],
            }],
        }
        result = summarize(snapshot)
        self.assertEqual(result["positions_market_value_by_currency"]["USD"]["amount"], "100.50")
        self.assertEqual(result["positions_market_value_by_currency"]["SGD"]["amount"], "50")
        self.assertEqual(result["position_rows_excluded_from_currency_totals"], 1)
        self.assertEqual(len(result["statements"][0]["cash_reports"]), 1)


if __name__ == "__main__":
    unittest.main()

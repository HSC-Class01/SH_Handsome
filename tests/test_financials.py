import importlib.util
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "update_financials.py"
spec = importlib.util.spec_from_file_location("update_financials", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class FinancialHelpersTests(unittest.TestCase):
    def test_amount_parser(self):
        self.assertEqual(module.amount("1,234"), 1234.0)
        self.assertEqual(module.amount("(450)"), -450.0)
        self.assertIsNone(module.amount("-"))

    def test_account_label_normalization(self):
        self.assertEqual(module.norm("당기 순이익 (손실)"), "당기순이익손실")

    def test_korean_account_matching(self):
        rows = [{"sj_div": "IS", "account_id": "custom_revenue", "account_nm": "매출액", "thstrm_amount": "1,234"}]
        self.assertEqual(module.pick(rows, "revenue"), 1234.0)

    def test_financial_ratios(self):
        rows = [{"revenue": 200.0, "operating_income": 20.0, "net_income": 10.0,
                 "assets": 150.0, "liabilities": 90.0, "equity": 60.0,
                 "current_assets": 40.0, "current_liabilities": 20.0, "report_no": None}]
        module.ratios(rows, 1)
        self.assertEqual(rows[0]["operating_margin"], 10.0)
        self.assertEqual(rows[0]["net_margin"], 5.0)
        self.assertEqual(rows[0]["debt_ratio"], 150.0)
        self.assertEqual(rows[0]["current_ratio"], 200.0)
        self.assertEqual(rows[0]["roe"], 16.67)

if __name__ == "__main__":
    unittest.main()

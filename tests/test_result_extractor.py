from core.result_extractor import extract_from_html
html = open("tests/fixtures/sample_tv_report.html", encoding="utf-8").read()
metrics = extract_from_html(html)
assert metrics["net_profit_pct"] == pytest.approx(12.34)

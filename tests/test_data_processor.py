from pathlib import Path

from src.data_processor import calculate_kpis, load_and_prepare


DATA = Path(__file__).parents[1] / "data" / "porsche_sales_sanitized.xlsx"


def test_dataset_reconciliation():
    df = load_and_prepare(DATA)
    kpis = calculate_kpis(df)

    assert kpis["records"] == 100
    assert kpis["valid_dates"] == 76
    assert kpis["invalid_dates"] == 24
    assert kpis["delivered_records"] == 41
    assert kpis["cancelled_records"] == 7
    assert kpis["top_family"] == "911"
    assert round(kpis["recorded_value"], 2) == 12_827_800.50


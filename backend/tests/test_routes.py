from src.app.main import app


def test_report_routes_match_public_api_contract():
    paths = app.openapi()["paths"]
    assert "/api/v1/reports" in paths
    assert "/api/v1/reports/{report_id}" in paths
    assert not any("/reports/reports" in path for path in paths)

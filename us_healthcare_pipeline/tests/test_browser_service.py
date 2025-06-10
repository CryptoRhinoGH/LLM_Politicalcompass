import json
import zipfile
from unittest.mock import MagicMock
from us_healthcare_pipeline.services.browser_service import BrowserService
from us_healthcare_pipeline.models.persona import Persona

def test_browser_service_creates_clean_metadata(tmp_path):
    import zipfile
    from unittest.mock import MagicMock
    from us_healthcare_pipeline.models.persona import Persona
    from us_healthcare_pipeline.services.browser_service import BrowserService

    dummy_zip_path = tmp_path / "dummy.zip"
    with zipfile.ZipFile(dummy_zip_path, 'w') as zipf:
        zipf.writestr("manifest.json", "{}")
        zipf.writestr("background.js", "//")

    mock_proxy = MagicMock()
    mock_proxy.session_id = "testsession"
    mock_proxy.create_proxy_extension.return_value = str(dummy_zip_path)

    persona = Persona(label="test", search_queries=["query"], news_sites=["https://example.com"])
    results_dir = tmp_path / "results" / "fixed"

    service = BrowserService(
        proxy_service=mock_proxy,
        persona=persona,
        city_name="Test City",
        base_results_dir=str(results_dir)
    )

    # Mock browser interactions
    service._get_ip_via_browser = MagicMock(return_value="123.45.67.89")
    service._write_llm_responses = MagicMock()

    # Patch _visit_url to simulate URL recording
    def mocked_visit_url(browser, url, wait_range=(3, 7)):
        service.visited_urls.append(url)

    service._visit_url = mocked_visit_url

    mock_llm = MagicMock()
    mock_llm.ask_questions.return_value = []

    questions = ["Test question?"]

    result, responses = service.run_full_session(mock_llm, questions)

    assert result.city_name == "test_city"
    assert result.visited_urls == [
        "https://www.google.com/search?q=query",
        "https://example.com"
    ]

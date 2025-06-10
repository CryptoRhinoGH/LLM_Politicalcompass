import json
import zipfile
from unittest.mock import MagicMock
from us_healthcare_pipeline.services.browser_service import BrowserService
from us_healthcare_pipeline.models.persona import Persona

def test_browser_service_creates_clean_metadata(tmp_path):
    dummy_zip_path = tmp_path / "dummy.zip"
    with zipfile.ZipFile(dummy_zip_path, 'w') as zipf:
        zipf.writestr("manifest.json", "{}")
        zipf.writestr("background.js", "//")

    mock_proxy = MagicMock()
    mock_proxy.session_id = "testsession"
    mock_proxy.create_proxy_extension.return_value = str(dummy_zip_path)

    persona = Persona(label="test", search_queries=["query"], news_sites=["https://example.com"])
    results_dir = tmp_path / "results" / "fixed"  # Simulated timestamp in path

    service = BrowserService(
        proxy_service=mock_proxy,
        persona=persona,
        city_name="Test City",
        base_results_dir=str(results_dir)
    )

    # Mock IP fetching and page visiting
    service._visit_url = MagicMock()
    service._get_ip_via_browser = MagicMock(return_value="123.45.67.89")

    mock_llm = MagicMock()
    mock_llm.ask_questions.return_value = []
    questions = ["Dummy?"]

    result, responses = service.run_full_session(mock_llm, questions)

    session_dir = results_dir / "test_city" / "test"
    assert session_dir.exists(), "Session directory not created"

    meta_path = session_dir.parent / "session_meta.json"
    assert meta_path.exists(), "Metadata file not created"

    with open(meta_path) as f:
        data = json.load(f)
        assert data["ip_address"] == "123.45.67.89"  # ✅ Now testable
        assert data["persona"] == "test"
        assert data["city"] == "test_city"
        assert isinstance(data["chrome_profile_quality"]["cookies_present"], bool)
        assert data["status"] == "success"
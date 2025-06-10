import os
import zipfile
import shutil
import random
import string
from us_healthcare_pipeline.config.cities import cities
from us_healthcare_pipeline.services.proxy_service import ProxyService

def random_session_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

def test_proxy_extension_creation():
    session_id = random_session_id()
    city = cities[0]
    proxy = ProxyService(city, session_id)
    base_path = ".proxy_extensions_test"

    zip_path = proxy.create_proxy_extension(base_path=base_path)

    assert os.path.isfile(zip_path)
    assert zip_path.endswith(".zip")

    # Check zip content
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        files = zipf.namelist()
        assert "manifest.json" in files
        assert "background.js" in files

    # Clean up (optional for test runs)
    shutil.rmtree(base_path)

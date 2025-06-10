import re
import random
import string
from us_healthcare_pipeline.services.proxy_service import ProxyService
from us_healthcare_pipeline.config.cities import cities

def random_session_id(length=8):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

def test_proxy_string_format():
    city = cities[0]
    session_id = random_session_id()
    proxy = ProxyService(city, session_id)
    proxy_str = proxy.get_proxy_string()

    assert proxy_str.startswith("http://")
    assert f"session-{session_id}" in proxy_str
    assert city.proxy_host in proxy_str
    assert str(city.proxy_port) in proxy_str

def test_proxy_dict_structure():
    city = cities[0]
    session_id = random_session_id()
    proxy = ProxyService(city, session_id)
    proxy_dict = proxy.get_proxy_dict()

    assert "http" in proxy_dict
    assert "https" in proxy_dict
    assert proxy_dict["http"].startswith("http://")
    assert f"session-{session_id}" in proxy_dict["http"]

# Optional: Live IP test (requires working Bright Data proxy)
# def test_get_session_ip():
#     city = cities[0]
#     session_id = random_session_id()
#     proxy = ProxyService(city, session_id)
#     ip = proxy.get_session_ip()
#     assert re.match(r"\d+\.\d+\.\d+\.\d+", ip)

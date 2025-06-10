from us_healthcare_pipeline.config.cities import cities

def test_city_list_structure():
    assert len(cities) > 0
    for city in cities:
        assert hasattr(city, "name")
        assert hasattr(city, "state")
        assert hasattr(city, "proxy_host")
        assert hasattr(city, "proxy_port")
        assert hasattr(city, "proxy_user")
        assert hasattr(city, "proxy_pass")
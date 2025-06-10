# models/city_proxy_list.py

from typing import List
from us_healthcare_pipeline.models.city import City
from us_healthcare_pipeline.config.cities import cities as loaded_cities


class CityProxyList:
    def __init__(self, cities: List[City] = loaded_cities):
        self._cities = cities

    def all(self) -> List[City]:
        return self._cities

    def get_by_name(self, name: str) -> City:
        for city in self._cities:
            if city.name.lower() == name.lower():
                return city
        raise ValueError(f"City '{name}' not found.")
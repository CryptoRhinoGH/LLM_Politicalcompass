from dataclasses import dataclass

@dataclass
class City:
    name: str
    state: str
    proxy_host: str
    proxy_port: int
    proxy_user: str
    proxy_pass: str

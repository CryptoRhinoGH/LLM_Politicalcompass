import os
import zipfile
from us_healthcare_pipeline.models.city import City

class ProxyService:
    def __init__(self, city: City, session_id: str):
        self.city = city
        self.session_id = session_id
        self.proxy_user = f"{city.proxy_user}-session-{session_id}"

    def get_proxy_dict(self) -> dict:
        proxy_auth = f"{self.proxy_user}:{self.city.proxy_pass}"
        proxy_url = f"http://{proxy_auth}@{self.city.proxy_host}:{self.city.proxy_port}"
        return {"http": proxy_url, "https": proxy_url}

    def get_proxy_string(self) -> str:
        return f"http://{self.proxy_user}:{self.city.proxy_pass}@{self.city.proxy_host}:{self.city.proxy_port}"

    def create_proxy_extension(self, base_path=".proxy_extensions") -> str:
        """
        Creates a Chrome extension to handle proxy authentication.

        Returns the path to the .zip file that should be loaded by Chrome.
        """
        proxy_host = self.city.proxy_host
        proxy_port = self.city.proxy_port
        proxy_user = self.proxy_user
        proxy_pass = self.city.proxy_pass

        session_dir = os.path.join(base_path, f"session_{self.session_id}")
        os.makedirs(session_dir, exist_ok=True)

        manifest_content = {
            "version": "1.0.0",
            "manifest_version": 2,
            "name": f"Proxy Extension {self.session_id}",
            "permissions": [
                "proxy",
                "tabs",
                "unlimitedStorage",
                "storage",
                "<all_urls>",
                "webRequest",
                "webRequestBlocking"
            ],
            "background": {
                "scripts": ["background.js"]
            }
        }

        background_script = f"""
chrome.proxy.settings.set({{
    value: {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: ["localhost"]
        }}
    }},
    scope: "regular"
}}, function() {{}});

chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_pass}"
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ['blocking']
);
"""

        # Write manifest.json
        manifest_path = os.path.join(session_dir, "manifest.json")
        with open(manifest_path, "w") as f:
            import json
            json.dump(manifest_content, f, indent=2)

        # Write background.js
        background_path = os.path.join(session_dir, "background.js")
        with open(background_path, "w") as f:
            f.write(background_script.strip())

        # Zip contents
        zip_path = os.path.join(session_dir, f"{self.session_id}.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            zipf.write(manifest_path, "manifest.json")
            zipf.write(background_path, "background.js")

        return zip_path
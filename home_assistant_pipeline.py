import os
from typing import List, Union, Generator, Iterator
import requests

class HomeAssistantAPI:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_api(self):
        url = f"{self.base_url}/api"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

class Pipeline:
    def __init__(self, base_url, token):
        self.name = "Home Assistant API Pipeline"
        self.api = HomeAssistantAPI(base_url, token)

    async def on_startup(self):
        print(f"on_startup: {self.name}")

    async def on_shutdown(self):
        print(f"on_shutdown: {self.name}")

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        print(f"pipe: {self.name}")
        print("Messages:", messages)
        print("User message:", user_message)

        if user_message.lower() == "get api":
            api_info = self.api.get_api()
            return str(api_info)
        else:
            return "Unrecognized message"

# Example usage
if __name__ == "__main__":
    base_url = os.getenv("HASS_BASE_URL", "http://your-home-assistant-url")
    token = os.getenv("HASS_TOKEN", "your-long-lived-access-token")

    pipeline = Pipeline(base_url, token)
    response = pipeline.pipe("get api", "", [], {})
    print(response)
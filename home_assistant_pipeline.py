import os
from typing import List, Union, Generator, Iterator
import requests

class HomeAssistantAPI:
    """
    Class to interact with the Home Assistant API.
    """

    def __init__(self, base_url, token):
        """
        Initialize with base URL and token.
        """
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def get_api(self):
        """
        Fetch the API details from Home Assistant.
        """
        url = f"{self.base_url}/api"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

class Pipeline:
    """
    Pipeline class for processing user messages and interacting with Home Assistant API.
    """

    def __init__(self, base_url, token):
        """
        Initialize the pipeline with Home Assistant base URL and token.
        """
        self.name = "Home Assistant API Pipeline"
        self.api = HomeAssistantAPI(base_url, token)

    async def on_startup(self):
        """
        Actions to perform when the server starts up.
        """
        print(f"on_startup: {self.name}")

    async def on_shutdown(self):
        """
        Actions to perform when the server shuts down.
        """
        print(f"on_shutdown: {self.name}")

    def pipe(self, user_message: str, model_id: str, messages: List[dict], body: dict) -> Union[str, Generator, Iterator]:
        """
        Process the user message and perform the appropriate API action.

        :param user_message: The message from the user.
        :param model_id: The model ID (not used in this example).
        :param messages: List of previous messages (not used in this example).
        :param body: Additional data for processing (not used in this example).
        :return: The response from the API or an unrecognized message error.
        """
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
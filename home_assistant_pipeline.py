import os
import requests
from typing import List, Union, Generator, Iterator
from pydantic import BaseModel, ValidationError

class Pipeline:
	class Valves(BaseModel):
		"""Defines environment variable configurations."""
		HOME_ASSISTANT_TOKEN: str = ""
		HOME_ASSISTANT_URL: str = ""

	class Tools:
		def __init__(self, pipeline) -> None:
			self.pipeline = pipeline

		def check_api_status(self) -> str:
			"""
			Check if the Home Assistant API is running.

			:return: A message indicating the API status.
			"""
			if not self.pipeline.valves.HOME_ASSISTANT_URL:
				return "Home Assistant URL not set, please configure it."
			
			headers = {
				"Authorization": f"Bearer {self.pipeline.valves.HOME_ASSISTANT_TOKEN}",
				"Content-Type": "application/json"
			}
			try:
				response = requests.get(f"{self.pipeline.valves.HOME_ASSISTANT_URL}/api/", headers=headers)
				response.raise_for_status()
				data = response.json()
				return f"API Status: {data['message']}"
			except requests.exceptions.HTTPError as http_err:
				return f"HTTP error occurred: {http_err}"
			except Exception as err:
				return f"An error occurred: {err}"

		def get_calendar_entities(self) -> str:
			"""
			Get the list of calendar entities from Home Assistant.

			:return: The list of calendar entities as a string.
			"""
			if not self.pipeline.valves.HOME_ASSISTANT_URL:
				return "Home Assistant URL not set, please configure it."

			headers = {
				"Authorization": f"Bearer {self.pipeline.valves.HOME_ASSISTANT_TOKEN}",
				"Content-Type": "application/json"
			}
			try:
				response = requests.get(f"{self.pipeline.valves.HOME_ASSISTANT_URL}/api/calendars", headers=headers)
				response.raise_for_status()
				data = response.json()
				entities = [f"{entity['name']} ({entity['entity_id']})" for entity in data]
				return "\n".join(entities)
			except requests.exceptions.HTTPError as http_err:
				return f"HTTP error occurred: {http_err}"
			except Exception as err:
				return f"An error occurred: {err}"

	def __init__(self):
		"""
		Initialize the Pipeline class.
		"""
		self.name = "Home Assistant API Pipeline"
		self.valves = self.Valves(
			**{
				"HOME_ASSISTANT_TOKEN": os.getenv("HOME_ASSISTANT_TOKEN", ""),
				"HOME_ASSISTANT_URL": os.getenv("HOME_ASSISTANT_URL", ""),
			},
		)
		self.tools = self.Tools(self)

	async def on_startup(self):
		"""
		Actions to perform when the server starts.
		"""
		print(f"on_startup: {__name__}")

	async def on_shutdown(self):
		"""
		Actions to perform when the server stops.
		"""
		print(f"on_shutdown: {__name__}")

	async def on_valves_updated(self):
		"""
		Actions to perform when the valves configuration is updated.
		"""
		pass

	async def inlet(self, body: dict, user: dict) -> dict:
		"""
		Modify the form data before it is sent to the OpenAI API.

		:param body: The request body.
		:param user: The user data.
		:return: The modified request body.
		"""
		print(f"inlet: {__name__}")
		print(body)
		print(user)
		return body

	async def outlet(self, body: dict, user: dict) -> dict:
		"""
		Modify the messages after they are received from the OpenAI API.

		:param body: The response body.
		:param user: The user data.
		:return: The modified response body.
		"""
		print(f"outlet: {__name__}")
		print(body)
		print(user)
		return body

	def pipe(self, user_message: str, model_id: str, messages: List[str], body: dict) -> Union[str, Generator, Iterator]:
		"""
		Process the user messages and return a response.

		:param user_message: The user's message.
		:param model_id: The model ID.
		:param messages: The list of messages.
		:param body: The request body.
		:return: The response as a string or an iterator.
		"""
		print(f"pipe: {__name__}")
		if user_message.lower() == "check api status":
			return self.tools.check_api_status()
		elif user_message.lower() == "get calendar entities":
			return self.tools.get_calendar_entities()
		return f"{__name__} response to: {user_message}"

# examples/scaffolds/home_assistant_pipeline.py
from blueprints.function_calling_blueprint import Pipeline as FunctionCallingBlueprint
import requests
import os
import ast

class Pipeline(FunctionCallingBlueprint):
	class Valves(FunctionCallingBlueprint.Valves):
		HOME_ASSISTANT_API_URL: str
		HOME_ASSISTANT_TOKEN: str

		def __init__(self):
			self.HOME_ASSISTANT_API_URL = os.getenv("HOME_ASSISTANT_API_URL", input("Enter Home Assistant API URL: "))
			self.HOME_ASSISTANT_TOKEN = os.getenv("HOME_ASSISTANT_TOKEN", input("Enter Home Assistant Token: "))

	class Tools:
		def __init__(self, pipeline) -> None:
			self.pipeline = pipeline

		def get_state(self, entity_id: str) -> dict:
			"""Get the state of an entity."""
			url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/states/{entity_id}"
			headers = self._get_headers()
			response = requests.get(url, headers=headers)
			response.raise_for_status()
			return response.json()

		def call_service(self, domain: str, service: str, service_data: dict) -> dict:
			"""Call a service."""
			url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/services/{domain}/{service}"
			headers = self._get_headers()
			response = requests.post(url, headers=headers, json=service_data)
			response.raise_for_status()
			return response.json()

		def get_all_states(self) -> dict:
			"""Get the states of all entities."""
			url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/states"
			headers = self._get_headers()
			response = requests.get(url, headers=headers)
			response.raise_for_status()
			return response.json()

		def get_events(self) -> dict:
			"""Get all available events."""
			url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/events"
			headers = self._get_headers()
			response = requests.get(url, headers=headers)
			response.raise_for_status()
			return response.json()

		def fire_event(self, event_type: str, event_data: dict) -> dict:
			"""Fire an event."""
			url = f"{self.pipeline.valves.HOME_ASSISTANT_API_URL}/api/events/{event_type}"
			headers = self._get_headers()
			response = requests.post(url, headers=headers, json=event_data)
			response.raise_for_status()
			return response.json()

		def calculator(self, equation: str) -> str:
			"""
			Calculate the result of an equation using safe evaluation.

			:param equation: The equation to calculate.
			"""
			try:
				result = ast.literal_eval(equation)
				return f"{equation} = {result}"
			except Exception as e:
				print(e)
				return "Invalid equation"

		def _get_headers(self) -> dict:
			"""Helper method to get headers."""
			return {
				"Authorization": f"Bearer {self.pipeline.valves.HOME_ASSISTANT_TOKEN}",
				"Content-Type": "application/json",
			}

	def __init__(self):
		super().__init__()
		self.name = "Home Assistant Pipeline"
		self.valves = self.Valves()
		self.tools = self.Tools(self)
